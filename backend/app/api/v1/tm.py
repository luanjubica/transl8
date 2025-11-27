from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from difflib import SequenceMatcher

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.tm import TranslationMemory
from app.schemas.tm import (
    TMEntryCreate,
    TMEntryResponse,
    TMMatchResponse,
    TMSearchRequest
)

router = APIRouter(prefix="/tm", tags=["translation-memory"])


@router.post("/search", response_model=List[TMMatchResponse])
def search_translation_memory(
    search_request: TMSearchRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search Translation Memory for matches.

    API-first design: Returns fuzzy matches with similarity scores.
    Uses Levenshtein distance for matching (can be improved with specialized libraries).

    Perfect for:
    - Pre-filling translations from previous work
    - Showing translators similar segments
    - Reducing AI translation costs
    """
    # TODO: Add org membership check

    # Get all TM entries for this language pair
    tm_entries = db.query(TranslationMemory).filter(
        and_(
            TranslationMemory.org_id == org_id,
            TranslationMemory.source_language == search_request.source_language,
            TranslationMemory.target_language == search_request.target_language
        )
    ).all()

    # Calculate similarity scores
    matches = []
    for entry in tm_entries:
        # Calculate similarity using SequenceMatcher
        score = SequenceMatcher(
            None,
            search_request.source_text.lower(),
            entry.source_text.lower()
        ).ratio()

        # Only include if above threshold
        if score >= search_request.min_score:
            matches.append(TMMatchResponse(
                source_text=entry.source_text,
                target_text=entry.target_text,
                match_score=score,
                source_language=entry.source_language,
                target_language=entry.target_language,
                tm_entry_id=entry.id
            ))

    # Sort by score (highest first) and limit results
    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches[:search_request.max_results]


@router.post("/entries", response_model=TMEntryResponse, status_code=status.HTTP_201_CREATED)
def create_tm_entry(
    entry_data: TMEntryCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an entry to Translation Memory.

    API-first design: Manually add translations to TM.
    Useful for importing existing translations or approved content.
    """
    # TODO: Add org membership check

    # Compute hash for fast exact matching
    source_hash = TranslationMemory.compute_hash(entry_data.source_text)

    # Check if entry already exists (avoid duplicates)
    existing = db.query(TranslationMemory).filter(
        and_(
            TranslationMemory.org_id == org_id,
            TranslationMemory.source_hash == source_hash,
            TranslationMemory.source_language == entry_data.source_language,
            TranslationMemory.target_language == entry_data.target_language
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="TM entry already exists for this source text and language pair"
        )

    tm_entry = TranslationMemory(
        org_id=org_id,
        source_language=entry_data.source_language,
        target_language=entry_data.target_language,
        source_text=entry_data.source_text,
        target_text=entry_data.target_text,
        source_hash=source_hash
    )

    db.add(tm_entry)
    db.commit()
    db.refresh(tm_entry)

    return TMEntryResponse.model_validate(tm_entry)


@router.get("/entries", response_model=List[TMEntryResponse])
def list_tm_entries(
    org_id: UUID = Query(..., description="Organization ID"),
    source_language: Optional[str] = Query(None, description="Filter by source language"),
    target_language: Optional[str] = Query(None, description="Filter by target language"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List Translation Memory entries.

    API-first design: Export TM for backups or migrations.
    """
    # TODO: Add org membership check

    query = db.query(TranslationMemory).filter(TranslationMemory.org_id == org_id)

    if source_language:
        query = query.filter(TranslationMemory.source_language == source_language)
    if target_language:
        query = query.filter(TranslationMemory.target_language == target_language)

    entries = query.offset(skip).limit(limit).all()

    return [TMEntryResponse.model_validate(entry) for entry in entries]


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tm_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a Translation Memory entry.

    API-first design: Remove outdated or incorrect TM entries.
    """
    entry = db.query(TranslationMemory).filter(TranslationMemory.id == entry_id).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TM entry not found"
        )

    # TODO: Add org membership check

    db.delete(entry)
    db.commit()

    return None
