from sqlalchemy import Column, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Project(Base):
    """
    Project model for organizing translation work.

    Each project has a source language and one or more target languages.
    Projects contain documents that need to be translated.
    """

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_language = Column(String(10), nullable=False)  # ISO 639-1: 'en', 'de', etc.
    target_languages = Column(ARRAY(String(10)), nullable=False)  # ['de', 'fr', 'nl']

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    creator = relationship("User")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name} ({self.source_language} → {self.target_languages})>"
