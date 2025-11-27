from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class TranslationJob(Base):
    """
    Translation job model for tracking async translation tasks.

    Jobs are created when triggering AI translation for a document.
    Status is updated by Celery workers as the job progresses.
    """

    __tablename__ = "translation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    target_language = Column(String(10), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    document = relationship("Document")

    def __repr__(self):
        return f"<TranslationJob {self.id} status={self.status} progress={self.progress}%>"
