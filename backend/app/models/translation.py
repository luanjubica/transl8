from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Translation(Base):
    """
    Translation model for translated segments.

    Each segment can have multiple translations (one per target language).
    Translations can be from AI, human translators, or TM matches.
    """

    __tablename__ = "translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id", ondelete="CASCADE"), nullable=False, index=True)
    target_language = Column(String(10), nullable=False)  # ISO 639-1 code
    translated_text = Column(Text, nullable=True)

    # Translation metadata
    status = Column(String(50), default="draft", nullable=False)  # draft, reviewed, approved
    translation_source = Column(String(50), nullable=True)  # ai, human, tm_match
    tm_match_score = Column(Float, nullable=True)  # 0.0 to 1.0

    # Quality checks
    length_exceeded = Column(Boolean, default=False, nullable=False)
    placeholder_valid = Column(Boolean, default=True, nullable=False)
    qa_warnings = Column(JSONB, nullable=True)  # List of QA warning messages

    # Audit trail
    translated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    segment = relationship("Segment", back_populates="translations")
    translator = relationship("User", foreign_keys=[translated_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    # Ensure unique translation per segment + language
    __table_args__ = (
        UniqueConstraint("segment_id", "target_language", name="uq_segment_language"),
    )

    def __repr__(self):
        preview = self.translated_text[:50] + "..." if self.translated_text and len(self.translated_text) > 50 else self.translated_text
        return f"<Translation {self.target_language}: {preview}>"
