from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class TMEntryBase(BaseModel):
    """Base schema for Translation Memory entry."""
    source_language: str = Field(..., min_length=2, max_length=10)
    target_language: str = Field(..., min_length=2, max_length=10)
    source_text: str
    target_text: str


class TMEntryCreate(TMEntryBase):
    """Schema for creating a TM entry."""
    pass


class TMEntryResponse(TMEntryBase):
    """Schema for TM entry responses."""
    id: UUID
    org_id: UUID
    source_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TMMatchResponse(BaseModel):
    """Schema for TM match results."""
    source_text: str
    target_text: str
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score from 0.0 to 1.0")
    source_language: str
    target_language: str
    tm_entry_id: UUID


class TMSearchRequest(BaseModel):
    """Schema for TM search request."""
    source_text: str
    source_language: str
    target_language: str
    min_score: float = Field(0.7, ge=0.0, le=1.0, description="Minimum match score threshold")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
