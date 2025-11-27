from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.segment import Segment
from app.schemas.segment import SegmentResponse

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("", response_model=List[SegmentResponse])
def list_segments(
    document_id: UUID = Query(..., description="Document ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all segments in a document.

    API-first design: Returns segments with placeholders and metadata.
    Supports pagination with skip/limit parameters.
    """
    # Verify document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # TODO: Add org membership check

    segments = db.query(Segment).filter(
        Segment.document_id == document_id
    ).order_by(Segment.index).offset(skip).limit(limit).all()

    return [SegmentResponse.model_validate(seg) for seg in segments]


@router.get("/{segment_id}", response_model=SegmentResponse)
def get_segment(
    segment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get segment details by ID.

    API-first design: Returns complete segment information including
    placeholders, tags, and metadata.
    """
    segment = db.query(Segment).filter(Segment.id == segment_id).first()

    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )

    # TODO: Add org membership check

    return SegmentResponse.model_validate(segment)


@router.patch("/{segment_id}/lock", response_model=SegmentResponse)
def lock_segment(
    segment_id: UUID,
    locked: bool = Query(..., description="Lock status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lock or unlock a segment.

    Locked segments are marked as "do not translate" and will be
    skipped by AI translation jobs.

    API-first design: Simple toggle endpoint for locking.
    """
    segment = db.query(Segment).filter(Segment.id == segment_id).first()

    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )

    # TODO: Add org membership check

    segment.is_locked = locked
    db.commit()
    db.refresh(segment)

    return SegmentResponse.model_validate(segment)
