from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID, uuid4

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.segment import Segment
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentUploadResponse
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    project_id: UUID = Query(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all documents in a project.

    API-first design: Returns documents with segment counts.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # TODO: Add org membership check

    documents = db.query(Document).filter(
        Document.project_id == project_id
    ).all()

    # Add segment counts
    document_responses = []
    for doc in documents:
        segment_count = db.query(func.count(Segment.id)).filter(
            Segment.document_id == doc.id
        ).scalar()

        doc_dict = DocumentResponse.model_validate(doc).model_dump()
        doc_dict['segment_count'] = segment_count
        document_responses.append(DocumentResponse(**doc_dict))

    return document_responses


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    project_id: UUID = Query(..., description="Project ID"),
    document_data: DocumentCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new document entry.

    API-first design: Returns document ID and upload instructions.
    File upload to S3 should be handled separately via pre-signed URLs.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # TODO: Add org membership check

    document = Document(
        project_id=project_id,
        name=document_data.name,
        file_type=document_data.file_type,
        file_url=document_data.file_url,
        file_size=document_data.file_size,
        file_schema=document_data.file_schema,
        placeholder_pattern=document_data.placeholder_pattern,
        max_segment_length=document_data.max_segment_length,
        uploaded_by=current_user.id,
        status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # TODO: Trigger Celery task to parse document

    return DocumentUploadResponse(
        document_id=document.id,
        message="Document created successfully. Processing will begin shortly."
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get document details by ID.

    API-first design: Returns full document information with segment count.
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # TODO: Add org membership check

    # Add segment count
    segment_count = db.query(func.count(Segment.id)).filter(
        Segment.document_id == document.id
    ).scalar()

    doc_dict = DocumentResponse.model_validate(document).model_dump()
    doc_dict['segment_count'] = segment_count

    return DocumentResponse(**doc_dict)


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update document metadata.

    API-first design: Partial updates supported via PATCH.
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # TODO: Add org membership check

    # Update only provided fields
    update_data = document_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    db.commit()
    db.refresh(document)

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document.

    API-first design: Cascade deletes all associated segments and translations.
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # TODO: Add org membership check
    # TODO: Delete file from S3

    db.delete(document)
    db.commit()

    return None
