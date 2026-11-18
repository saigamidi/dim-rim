"""VIN record model for extracted and normalized VINs."""
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.candidate_row import CandidateRow
    from app.models.intake_case import IntakeCase
    from app.models.vin_validation_result import VinValidationResult


class VinRecord(Base):
    """VIN record model storing extracted VINs with normalization and deduplication."""

    __tablename__ = "vin_record"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intake_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("intake_case.id"), nullable=False, index=True
    )
    candidate_row_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidate_row.id"), nullable=False, index=True
    )
    raw_vin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    normalized_vin: Mapped[str | None] = mapped_column(String(17), nullable=True, index=True)
    extraction_status: Mapped[str] = mapped_column(String(64), nullable=False)
    is_duplicate_within_case: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    intake_case: Mapped["IntakeCase"] = relationship(back_populates="vin_records")
    candidate_row: Mapped["CandidateRow"] = relationship(back_populates="vin_records")
    validation_result: Mapped["VinValidationResult | None"] = relationship(
        back_populates="vin_record", cascade="all, delete-orphan", uselist=False
    )
