from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class TranslationCreate(BaseModel):
    """Schema for creating a translation."""
    translated_text: str
    target_language: str = Field(..., min_length=2, max_length=10)
    translation_source: Optional[str] = "human"


class TranslationUpdate(BaseModel):
    """Schema for updating a translation."""
    translated_text: Optional[str] = None
    status: Optional[str] = None


class TranslationResponse(BaseModel):
    """Schema for translation responses."""
    id: UUID
    segment_id: UUID
    target_language: str
    translated_text: Optional[str]
    status: str
    translation_source: Optional[str]
    tm_match_score: Optional[float]
    length_exceeded: bool
    placeholder_valid: bool
    qa_warnings: Optional[Dict[str, Any]]
    translated_by: Optional[UUID]
    reviewed_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
