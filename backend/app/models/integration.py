from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Integration(Base):
    """
    Integration model for external connections.

    Stores configuration for API keys, PIM connections, webhooks, etc.
    Credentials are encrypted before storage.
    """

    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # api_key, pim_akeneo, pim_salsify, webhook
    name = Column(String(255), nullable=False)
    config = Column(JSONB, nullable=True)  # Encrypted credentials, endpoints, settings

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization")

    def __repr__(self):
        return f"<Integration {self.name} ({self.type})>"
