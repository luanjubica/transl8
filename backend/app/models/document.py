from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Document(Base):
    """
    Document model for uploaded files.

    Documents are parsed to extract segments (translatable units).
    Supports various file types: XML, XLIFF, JSON, CSV, XLSX, DOCX, PDF.
    """

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # xml, xliff, json, csv, xlsx, docx, pdf
    file_url = Column(String(500), nullable=False)  # S3/R2 URL
    file_size = Column(Integer, nullable=True)
    status = Column(String(50), default="uploaded", nullable=False)  # uploaded, processing, ready, error

    # File parsing metadata
    file_schema = Column(String(500), nullable=True)  # XSD path or schema identifier
    placeholder_pattern = Column(String(255), nullable=True)  # Regex for detecting variables
    max_segment_length = Column(Integer, nullable=True)  # For label length constraints

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="documents")
    uploader = relationship("User")
    segments = relationship("Segment", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.name} ({self.file_type})>"
