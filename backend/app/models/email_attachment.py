"""Email attachment model for parsed attachments."""
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.candidate_row import CandidateRow
    from app.models.intake_case import IntakeCase


class EmailAttachment(Base):
    """Email attachment model storing attachment metadata and parse status."""

    __tablename__ = "email_attachment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intake_case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("intake_case.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(128), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    parse_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    intake_case: Mapped["IntakeCase"] = relationship(back_populates="attachments")
    candidate_rows: Mapped[list["CandidateRow"]] = relationship(
        back_populates="attachment", cascade="all, delete-orphan"
    )
