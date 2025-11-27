from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.glossary import Glossary, GlossaryTerm
from app.schemas.glossary import (
    GlossaryCreate,
    GlossaryUpdate,
    GlossaryResponse,
    GlossaryTermCreate,
    GlossaryTermUpdate,
    GlossaryTermResponse,
    GlossaryImportRequest
)

router = APIRouter(prefix="/glossaries", tags=["glossaries"])


@router.get("", response_model=List[GlossaryResponse])
def list_glossaries(
    org_id: UUID = Query(..., description="Organization ID"),
    source_language: Optional[str] = Query(None, description="Filter by source language"),
    target_language: Optional[str] = Query(None, description="Filter by target language"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all glossaries in an organization.

    API-first design: Returns glossaries with term counts.
    Supports filtering by language pairs.
    """
    # TODO: Add org membership check

    # Build query
    query = db.query(Glossary).filter(Glossary.org_id == org_id)

    if source_language:
        query = query.filter(Glossary.source_language == source_language)
    if target_language:
        query = query.filter(Glossary.target_language == target_language)

    glossaries = query.all()

    # Add term counts
    glossary_responses = []
    for glossary in glossaries:
        term_count = db.query(func.count(GlossaryTerm.id)).filter(
            GlossaryTerm.glossary_id == glossary.id
        ).scalar()

        glossary_dict = GlossaryResponse.model_validate(glossary).model_dump()
        glossary_dict['term_count'] = term_count
        glossary_responses.append(GlossaryResponse(**glossary_dict))

    return glossary_responses


@router.post("", response_model=GlossaryResponse, status_code=status.HTTP_201_CREATED)
def create_glossary(
    glossary_data: GlossaryCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new glossary.

    API-first design: Create glossaries programmatically for API integrations.
    """
    # TODO: Add org membership check

    glossary = Glossary(
        org_id=org_id,
        name=glossary_data.name,
        source_language=glossary_data.source_language,
        target_language=glossary_data.target_language
    )

    db.add(glossary)
    db.commit()
    db.refresh(glossary)

    return GlossaryResponse.model_validate(glossary)


@router.get("/{glossary_id}", response_model=GlossaryResponse)
def get_glossary(
    glossary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get glossary details by ID.

    API-first design: Returns glossary with term count.
    """
    glossary = db.query(Glossary).filter(Glossary.id == glossary_id).first()

    if not glossary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Glossary not found"
        )

    # TODO: Add org membership check

    # Add term count
    term_count = db.query(func.count(GlossaryTerm.id)).filter(
        GlossaryTerm.glossary_id == glossary.id
    ).scalar()

    glossary_dict = GlossaryResponse.model_validate(glossary).model_dump()
    glossary_dict['term_count'] = term_count

    return GlossaryResponse(**glossary_dict)


@router.patch("/{glossary_id}", response_model=GlossaryResponse)
def update_glossary(
    glossary_id: UUID,
    glossary_data: GlossaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update glossary metadata.

    API-first design: Partial updates supported.
    """
    glossary = db.query(Glossary).filter(Glossary.id == glossary_id).first()

    if not glossary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Glossary not found"
        )

    # TODO: Add org membership check

    update_data = glossary_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(glossary, field, value)

    db.commit()
    db.refresh(glossary)

    return GlossaryResponse.model_validate(glossary)


@router.delete("/{glossary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_glossary(
    glossary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a glossary.

    API-first design: Cascade deletes all terms.
    """
    glossary = db.query(Glossary).filter(Glossary.id == glossary_id).first()

    if not glossary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Glossary not found"
        )

    # TODO: Add org membership check

    db.delete(glossary)
    db.commit()

    return None


# Glossary Terms endpoints
@router.get("/{glossary_id}/terms", response_model=List[GlossaryTermResponse])
def list_glossary_terms(
    glossary_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List terms in a glossary.

    API-first design: Paginated term listing.
    """
    # Verify glossary exists
    glossary = db.query(Glossary).filter(Glossary.id == glossary_id).first()
    if not glossary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Glossary not found"
        )

    # TODO: Add org membership check

    terms = db.query(GlossaryTerm).filter(
        GlossaryTerm.glossary_id == glossary_id
    ).offset(skip).limit(limit).all()

    return [GlossaryTermResponse.model_validate(term) for term in terms]


@router.post("/{glossary_id}/terms", response_model=GlossaryTermResponse, status_code=status.HTTP_201_CREATED)
def create_glossary_term(
    glossary_id: UUID,
    term_data: GlossaryTermCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a term to a glossary.

    API-first design: Programmatic term addition.
    """
    # Verify glossary exists
    glossary = db.query(Glossary).filter(Glossary.id == glossary_id).first()
    if not glossary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Glossary not found"
        )

    # TODO: Add org membership check

    term = GlossaryTerm(
        glossary_id=glossary_id,
        source_term=term_data.source_term,
        target_term=term_data.target_term,
        notes=term_data.notes
    )

    db.add(term)
    db.commit()
    db.refresh(term)

    return GlossaryTermResponse.model_validate(term)


@router.post("/{glossary_id}/terms/import", response_model=dict)
def import_glossary_terms(
    glossary_id: UUID,
    import_data: GlossaryImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk import terms into a glossary.

    API-first design: Allows importing terms from external systems.
    Useful for PIM integrations and data migrations.
    """
    # Verify glossary exists
    glossary = db.query(Glossary).filter(Glossary.id == glossary_id).first()
    if not glossary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Glossary not found"
        )

    # TODO: Add org membership check

    imported_count = 0
    skipped_count = 0

    for term_data in import_data.terms:
        # Check for duplicates if skip_duplicates is True
        if import_data.skip_duplicates:
            existing = db.query(GlossaryTerm).filter(
                and_(
                    GlossaryTerm.glossary_id == glossary_id,
                    GlossaryTerm.source_term == term_data.source_term
                )
            ).first()

            if existing:
                skipped_count += 1
                continue

        term = GlossaryTerm(
            glossary_id=glossary_id,
            source_term=term_data.source_term,
            target_term=term_data.target_term,
            notes=term_data.notes
        )
        db.add(term)
        imported_count += 1

    db.commit()

    return {
        "message": "Terms imported successfully",
        "imported": imported_count,
        "skipped": skipped_count,
        "total": len(import_data.terms)
    }


@router.patch("/{glossary_id}/terms/{term_id}", response_model=GlossaryTermResponse)
def update_glossary_term(
    glossary_id: UUID,
    term_id: UUID,
    term_data: GlossaryTermUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a glossary term.

    API-first design: Partial updates supported.
    """
    term = db.query(GlossaryTerm).filter(
        and_(
            GlossaryTerm.id == term_id,
            GlossaryTerm.glossary_id == glossary_id
        )
    ).first()

    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found"
        )

    # TODO: Add org membership check

    update_data = term_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(term, field, value)

    db.commit()
    db.refresh(term)

    return GlossaryTermResponse.model_validate(term)


@router.delete("/{glossary_id}/terms/{term_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_glossary_term(
    glossary_id: UUID,
    term_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a glossary term.

    API-first design: Programmatic term deletion.
    """
    term = db.query(GlossaryTerm).filter(
        and_(
            GlossaryTerm.id == term_id,
            GlossaryTerm.glossary_id == glossary_id
        )
    ).first()

    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term not found"
        )

    # TODO: Add org membership check

    db.delete(term)
    db.commit()

    return None
