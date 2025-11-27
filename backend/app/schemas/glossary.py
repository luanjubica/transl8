from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class GlossaryBase(BaseModel):
    """Base schema for glossary data."""
    name: str = Field(..., min_length=1, max_length=255)
    source_language: str = Field(..., min_length=2, max_length=10)
    target_language: str = Field(..., min_length=2, max_length=10)


class GlossaryCreate(GlossaryBase):
    """Schema for creating a glossary."""
    pass


class GlossaryUpdate(BaseModel):
    """Schema for updating a glossary."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class GlossaryResponse(GlossaryBase):
    """Schema for glossary responses."""
    id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: datetime
    term_count: Optional[int] = None  # Computed field

    class Config:
        from_attributes = True


class GlossaryTermBase(BaseModel):
    """Base schema for glossary term data."""
    source_term: str = Field(..., min_length=1, max_length=500)
    target_term: str = Field(..., min_length=1, max_length=500)
    notes: Optional[str] = None


class GlossaryTermCreate(GlossaryTermBase):
    """Schema for creating a glossary term."""
    pass


class GlossaryTermUpdate(BaseModel):
    """Schema for updating a glossary term."""
    source_term: Optional[str] = Field(None, min_length=1, max_length=500)
    target_term: Optional[str] = Field(None, min_length=1, max_length=500)
    notes: Optional[str] = None


class GlossaryTermResponse(GlossaryTermBase):
    """Schema for glossary term responses."""
    id: UUID
    glossary_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlossaryImportRequest(BaseModel):
    """Schema for bulk glossary term import."""
    terms: List[GlossaryTermCreate]
    skip_duplicates: bool = True
