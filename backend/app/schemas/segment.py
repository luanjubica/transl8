from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class SegmentBase(BaseModel):
    """Base schema for segment data."""
    source_text: str
    context: Optional[str] = None
    max_length: Optional[int] = None
    is_locked: bool = False


class SegmentResponse(SegmentBase):
    """Schema for segment responses."""
    id: UUID
    document_id: UUID
    index: int
    char_count: Optional[int]
    word_count: Optional[int]
    placeholders: Optional[Dict[str, Any]]
    tags: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
