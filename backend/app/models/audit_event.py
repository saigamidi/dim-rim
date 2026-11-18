"""Audit event model for append-only audit trail."""
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.intake_case import IntakeCase


class AuditEvent(Base):
    """Audit event model for append-only governance record."""

    __tablename__ = "audit_event"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intake_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("intake_case.id"), nullable=False, index=True
    )
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    action_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    outcome: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at_utc: Mapped[datetime] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    intake_case: Mapped["IntakeCase"] = relationship(back_populates="audit_events")
