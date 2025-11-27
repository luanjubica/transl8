from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class DocumentBase(BaseModel):
    """Base schema for document data."""
    name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., description="xml, xliff, json, csv, xlsx, docx, pdf")


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    file_url: str
    file_size: Optional[int] = None
    file_schema: Optional[str] = None
    placeholder_pattern: Optional[str] = None
    max_segment_length: Optional[int] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None
    placeholder_pattern: Optional[str] = None
    max_segment_length: Optional[int] = None


class DocumentResponse(DocumentBase):
    """Schema for document responses."""
    id: UUID
    project_id: UUID
    file_url: str
    file_size: Optional[int]
    status: str
    file_schema: Optional[str]
    placeholder_pattern: Optional[str]
    max_segment_length: Optional[int]
    uploaded_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    segment_count: Optional[int] = None  # Computed field

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    document_id: UUID
    upload_url: Optional[str] = None  # Pre-signed S3 URL for upload
    message: str
