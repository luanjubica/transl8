from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class ProjectBase(BaseModel):
    """Base schema for project data."""
    name: str = Field(..., min_length=1, max_length=255)
    source_language: str = Field(..., min_length=2, max_length=10, description="ISO 639-1 code")
    target_languages: List[str] = Field(..., min_items=1, description="List of ISO 639-1 codes")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    source_language: Optional[str] = Field(None, min_length=2, max_length=10)
    target_languages: Optional[List[str]] = Field(None, min_items=1)


class ProjectResponse(ProjectBase):
    """Schema for project responses."""
    id: UUID
    org_id: UUID
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    document_count: Optional[int] = None  # Computed field

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for paginated project list."""
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
