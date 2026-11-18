"""Candidate row model for parsed attachment rows."""
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.email_attachment import EmailAttachment
    from app.models.vin_record import VinRecord


class CandidateRow(Base):
    """Candidate row model storing parsed canonical rows with lineage."""

    __tablename__ = "candidate_row"
    __table_args__ = (UniqueConstraint("attachment_id", "source_row_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    attachment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("email_attachment.id"), nullable=False, index=True
    )
    source_row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    canonical_vin_candidate: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_row_json: Mapped[str] = mapped_column(Text, nullable=False)
    row_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    lineage_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    attachment: Mapped["EmailAttachment"] = relationship(back_populates="candidate_rows")
    vin_records: Mapped[list["VinRecord"]] = relationship(
        back_populates="candidate_row", cascade="all, delete-orphan"
    )
