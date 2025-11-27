from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.job import TranslationJob
from app.schemas.job import JobCreate, JobResponse, JobStatusUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_translation_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a translation job for a document.

    API-first design: Trigger AI translation programmatically.
    Returns job ID for status tracking.

    Perfect for:
    - Automating translations via CI/CD
    - Batch processing multiple documents
    - Integrating with external workflows
    """
    # Verify document exists
    document = db.query(Document).filter(Document.id == job_data.document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # TODO: Add org membership check
    # TODO: Verify target_language is in project's target_languages

    # Check if job already exists for this document + language
    existing_job = db.query(TranslationJob).filter(
        TranslationJob.document_id == job_data.document_id,
        TranslationJob.target_language == job_data.target_language,
        TranslationJob.status.in_(["pending", "processing"])
    ).first()

    if existing_job:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Translation job already in progress for this document and language"
        )

    job = TranslationJob(
        document_id=job_data.document_id,
        target_language=job_data.target_language,
        status="pending",
        progress=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # TODO: Queue Celery task to process translation

    return JobResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get translation job status.

    API-first design: Poll for job completion status.
    Returns progress percentage and current status.

    Status values:
    - pending: Job is queued
    - processing: Translation in progress
    - completed: Job finished successfully
    - failed: Job encountered an error
    """
    job = db.query(TranslationJob).filter(TranslationJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # TODO: Add org membership check

    return JobResponse.model_validate(job)


@router.get("", response_model=List[JobResponse])
def list_jobs(
    document_id: Optional[UUID] = Query(None, description="Filter by document ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List translation jobs.

    API-first design: Monitor all translation jobs.
    Useful for dashboards and job management.
    """
    # TODO: Add org membership check

    query = db.query(TranslationJob)

    if document_id:
        query = query.filter(TranslationJob.document_id == document_id)

    if status_filter:
        query = query.filter(TranslationJob.status == status_filter)

    jobs = query.order_by(TranslationJob.created_at.desc()).offset(skip).limit(limit).all()

    return [JobResponse.model_validate(job) for job in jobs]


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a translation job.

    API-first design: Abort in-progress translations.
    Only works for pending or processing jobs.
    """
    job = db.query(TranslationJob).filter(TranslationJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # TODO: Add org membership check

    if job.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status '{job.status}'"
        )

    job.status = "failed"
    job.error_message = "Job cancelled by user"
    job.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(job)

    # TODO: Cancel Celery task

    return JobResponse.model_validate(job)


@router.patch("/{job_id}/status", response_model=JobResponse)
def update_job_status(
    job_id: UUID,
    status_update: JobStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update job status (internal endpoint for Celery workers).

    API-first design: Workers update progress via API.
    Could be protected with internal API key in production.
    """
    job = db.query(TranslationJob).filter(TranslationJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Update status
    if status_update.status:
        job.status = status_update.status

        if status_update.status == "processing" and not job.started_at:
            job.started_at = datetime.utcnow()

        if status_update.status in ["completed", "failed"]:
            job.completed_at = datetime.utcnow()

    if status_update.progress is not None:
        job.progress = status_update.progress

    if status_update.error_message:
        job.error_message = status_update.error_message

    db.commit()
    db.refresh(job)

    return JobResponse.model_validate(job)
