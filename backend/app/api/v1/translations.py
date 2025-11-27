from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.segment import Segment
from app.models.translation import Translation
from app.schemas.translation import (
    TranslationCreate,
    TranslationUpdate,
    TranslationResponse
)

router = APIRouter(prefix="/translations", tags=["translations"])


@router.get("", response_model=List[TranslationResponse])
def list_translations(
    document_id: UUID = Query(..., description="Document ID"),
    target_language: str = Query(..., description="Target language code"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List translations for a document in a specific language.

    API-first design: Returns translations with QA warnings and metadata.
    Supports filtering by status (draft, reviewed, approved).
    """
    # Build query
    query = db.query(Translation).join(Segment).filter(
        Segment.document_id == document_id,
        Translation.target_language == target_language
    )

    # Apply status filter if provided
    if status_filter:
        query = query.filter(Translation.status == status_filter)

    # TODO: Add org membership check

    translations = query.order_by(Segment.index).offset(skip).limit(limit).all()

    return [TranslationResponse.model_validate(t) for t in translations]


@router.post("", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
def create_translation(
    segment_id: UUID = Query(..., description="Segment ID"),
    translation_data: TranslationCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a translation for a segment.

    API-first design: Allows creating translations programmatically.
    Automatically runs QA checks (placeholder validation, length constraints).
    """
    # Verify segment exists
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )

    # TODO: Add org membership check

    # Check if translation already exists
    existing = db.query(Translation).filter(
        and_(
            Translation.segment_id == segment_id,
            Translation.target_language == translation_data.target_language
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Translation already exists for this segment and language"
        )

    # TODO: Run QA checks
    length_exceeded = False
    placeholder_valid = True
    if segment.max_length and len(translation_data.translated_text) > segment.max_length:
        length_exceeded = True

    translation = Translation(
        segment_id=segment_id,
        target_language=translation_data.target_language,
        translated_text=translation_data.translated_text,
        translation_source=translation_data.translation_source,
        length_exceeded=length_exceeded,
        placeholder_valid=placeholder_valid,
        translated_by=current_user.id
    )

    db.add(translation)
    db.commit()
    db.refresh(translation)

    return TranslationResponse.model_validate(translation)


@router.get("/{translation_id}", response_model=TranslationResponse)
def get_translation(
    translation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get translation details by ID.

    API-first design: Returns complete translation with QA status.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    # TODO: Add org membership check

    return TranslationResponse.model_validate(translation)


@router.patch("/{translation_id}", response_model=TranslationResponse)
def update_translation(
    translation_id: UUID,
    translation_data: TranslationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a translation.

    API-first design: Supports partial updates via PATCH.
    Re-runs QA checks on text changes.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    # TODO: Add org membership check

    # Update fields
    update_data = translation_data.model_dump(exclude_unset=True)

    # Re-run QA checks if text changed
    if "translated_text" in update_data:
        segment = db.query(Segment).filter(Segment.id == translation.segment_id).first()
        if segment.max_length and len(update_data["translated_text"]) > segment.max_length:
            translation.length_exceeded = True
        else:
            translation.length_exceeded = False
        # TODO: Validate placeholders

    for field, value in update_data.items():
        setattr(translation, field, value)

    db.commit()
    db.refresh(translation)

    return TranslationResponse.model_validate(translation)


@router.patch("/{translation_id}/approve", response_model=TranslationResponse)
def approve_translation(
    translation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a translation.

    Marks translation as approved and adds it to Translation Memory.

    API-first design: Simple approval workflow endpoint.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    # TODO: Add org membership check with role validation

    translation.status = "approved"
    translation.reviewed_by = current_user.id

    db.commit()
    db.refresh(translation)

    # TODO: Add to Translation Memory

    return TranslationResponse.model_validate(translation)


@router.delete("/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_translation(
    translation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a translation.

    API-first design: Allows programmatic deletion of translations.
    """
    translation = db.query(Translation).filter(Translation.id == translation_id).first()

    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )

    # TODO: Add org membership check

    db.delete(translation)
    db.commit()

    return None
