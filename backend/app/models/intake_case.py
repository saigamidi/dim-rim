"""Intake case model for disruption email submissions."""
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.audit_event import AuditEvent
    from app.models.classification_decision import ClassificationDecision
    from app.models.email_attachment import EmailAttachment
    from app.models.vin_record import VinRecord


class IntakeCase(Base):
    """Intake case model storing receipt metadata for disruption email candidates."""

    __tablename__ = "intake_case"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    source_email_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    source_address: Mapped[str] = mapped_column(String(320), nullable=False)
    received_at_utc: Mapped[datetime] = mapped_column(nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(512), nullable=False)
    intake_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    attachments: Mapped[list["EmailAttachment"]] = relationship(
        back_populates="intake_case", cascade="all, delete-orphan"
    )
    classification_decisions: Mapped[list["ClassificationDecision"]] = relationship(
        back_populates="intake_case", cascade="all, delete-orphan"
    )
    vin_records: Mapped[list["VinRecord"]] = relationship(
        back_populates="intake_case", cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="intake_case", cascade="all, delete-orphan"
    )
