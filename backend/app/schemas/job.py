from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class JobBase(BaseModel):
    """Base schema for translation job."""
    target_language: str = Field(..., min_length=2, max_length=10)


class JobCreate(JobBase):
    """Schema for creating a translation job."""
    document_id: UUID


class JobResponse(BaseModel):
    """Schema for job responses."""
    id: UUID
    document_id: UUID
    target_language: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobStatusUpdate(BaseModel):
    """Schema for updating job status (internal use)."""
    status: str
    progress: Optional[int] = None
    error_message: Optional[str] = None
