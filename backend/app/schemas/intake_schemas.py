"""Intake domain schemas for request/response DTOs."""
from datetime import datetime

from pydantic import BaseModel, Field


class InboxSubmissionIn(BaseModel):
    """Inbox submission request schema."""

    source_email_id: str = Field(..., description="Unique email ID from inbox connector")
    source_address: str = Field(..., max_length=320, description="From address")
    received_at_utc: datetime = Field(..., description="Email receipt timestamp (UTC)")
    subject: str = Field(..., max_length=512, description="Email subject line")
    has_attachments: bool = Field(..., description="Whether email has attachments")


class AttachmentOut(BaseModel):
    """Email attachment response schema."""

    id: str
    intake_case_id: str
    filename: str
    media_type: str
    byte_size: int
    storage_ref: str
    parse_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntakeCaseOut(BaseModel):
    """Intake case response schema."""

    id: str
    case_key: str
    source_email_id: str
    source_address: str
    received_at_utc: datetime
    subject: str
    intake_status: str
    correlation_id: str
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentOut] = []

    class Config:
        from_attributes = True
