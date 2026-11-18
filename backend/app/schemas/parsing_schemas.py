"""Parsing domain schemas for attachment parsing and candidate row management."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttachmentParseRequest(BaseModel):
    """Request schema for attachment parse operation."""

    force_reparse: bool = Field(default=False, description="Force reparse of already parsed attachment")


class AttachmentParseResultOut(BaseModel):
    """Response schema for attachment parse operation."""

    attachment_id: str
    parse_status: str
    row_count: int
    failure_count: int
    lineage_base_ref: str

    model_config = ConfigDict(from_attributes=True)


class CandidateRowOut(BaseModel):
    """Response schema for candidate row."""

    id: str
    attachment_id: str
    source_row_number: int
    canonical_vin_candidate: str | None
    raw_row_json: str
    row_status: str
    lineage_ref: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
