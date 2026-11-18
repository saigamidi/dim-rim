"""Audit domain schemas for request/response DTOs."""
from datetime import datetime

from pydantic import BaseModel


class AuditEventOut(BaseModel):
    """Audit event response schema."""

    id: str
    intake_case_id: str
    correlation_id: str
    actor_type: str
    actor_id: str
    action_type: str
    entity_type: str
    entity_id: str
    outcome: str
    metadata_json: str
    occurred_at_utc: datetime
    created_at: datetime

    class Config:
        from_attributes = True
