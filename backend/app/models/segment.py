from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Segment(Base):
    """
    Segment model for translatable units.

    Segments are extracted from documents during parsing.
    Each segment contains source text and metadata like placeholders, tags, context.
    """

    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    index = Column(Integer, nullable=False)  # Order in document
    source_text = Column(Text, nullable=False)

    # Text metrics
    char_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)  # Per-segment character limit

    # Flags
    is_locked = Column(Boolean, default=False, nullable=False)  # Do not translate

    # Metadata
    context = Column(Text, nullable=True)  # From XML comments/attributes
    placeholders = Column(JSONB, nullable=True)  # Detected variables: ["{name}", "%s"]
    tags = Column(JSONB, nullable=True)  # Inline formatting tags
    metadata = Column(JSONB, nullable=True)  # Additional context

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="segments")
    translations = relationship("Translation", back_populates="segment", cascade="all, delete-orphan")

    def __repr__(self):
        preview = self.source_text[:50] + "..." if len(self.source_text) > 50 else self.source_text
        return f"<Segment {self.index}: {preview}>"
