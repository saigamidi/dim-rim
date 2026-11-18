"""Classification decision model for human-gated disruption classification."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.intake_case import IntakeCase


class ClassificationDecision(Base):
    """Classification decision model for reviewer confirm/revise/reject actions."""

    __tablename__ = "classification_decision"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intake_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("intake_case.id"), nullable=False, index=True
    )
    suggested_disruption_type: Mapped[str] = mapped_column(String(128), nullable=False)
    suggested_disruption_subtype: Mapped[str | None] = mapped_column(String(128), nullable=True)
    suggested_event_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    reviewer_decision: Mapped[str] = mapped_column(String(32), nullable=False)
    final_disruption_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    final_disruption_subtype: Mapped[str | None] = mapped_column(String(128), nullable=True)
    final_event_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewer_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by_user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    decided_at_utc: Mapped[datetime] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    intake_case: Mapped["IntakeCase"] = relationship(back_populates="classification_decisions")
