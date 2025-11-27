from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Glossary(Base):
    """
    Glossary model for term databases.

    Glossaries ensure consistent terminology across translations.
    Each glossary is specific to a language pair and organization.
    """

    __tablename__ = "glossaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="glossaries")
    terms = relationship("GlossaryTerm", back_populates="glossary", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Glossary {self.name} ({self.source_language} → {self.target_language})>"


class GlossaryTerm(Base):
    """
    Glossary term model for individual term pairs.

    Each term maps a source word/phrase to its target translation.
    """

    __tablename__ = "glossary_terms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    glossary_id = Column(UUID(as_uuid=True), ForeignKey("glossaries.id", ondelete="CASCADE"), nullable=False, index=True)
    source_term = Column(String(500), nullable=False)
    target_term = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    glossary = relationship("Glossary", back_populates="terms")

    def __repr__(self):
        return f"<GlossaryTerm {self.source_term} → {self.target_term}>"
