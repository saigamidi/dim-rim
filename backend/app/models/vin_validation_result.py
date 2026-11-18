"""VIN validation result model for BR-01 deterministic validation outcomes."""
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.vin_record import VinRecord


class VinValidationResult(Base):
    """VIN validation result model storing BR-01 validation outcomes with explicit failure reasons."""

    __tablename__ = "vin_validation_result"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vin_record_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vin_record.id"), unique=True, nullable=False, index=True
    )
    validation_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    failure_reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    failure_reason_detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    checksum_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    validated_at_utc: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    vin_record: Mapped["VinRecord"] = relationship(back_populates="validation_result")
