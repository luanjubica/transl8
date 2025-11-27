from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import hashlib
from app.core.database import Base


class TranslationMemory(Base):
    """
    Translation Memory (TM) model.

    Stores previously translated segments for reuse.
    Uses hash-based indexing for fast matching.
    """

    __tablename__ = "translation_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    source_text = Column(Text, nullable=False)
    target_text = Column(Text, nullable=False)
    source_hash = Column(String(64), nullable=False, index=True)  # SHA256 hash for fast matching

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Composite index for efficient lookups
    __table_args__ = (
        Index("idx_tm_org_langs", "org_id", "source_language", "target_language"),
        Index("idx_tm_hash", "source_hash"),
    )

    @staticmethod
    def compute_hash(text: str) -> str:
        """
        Compute SHA256 hash of source text for fast matching.

        Args:
            text: Source text to hash

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def __repr__(self):
        source_preview = self.source_text[:50] + "..." if len(self.source_text) > 50 else self.source_text
        return f"<TM {self.source_language}→{self.target_language}: {source_preview}>"
