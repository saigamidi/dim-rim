"""Classification domain schemas for request/response DTOs."""
from datetime import datetime

from pydantic import BaseModel, Field


class ClassificationRecommendationOut(BaseModel):
    """AI-assisted classification recommendation response schema."""

    id: str
    intake_case_id: str
    suggested_disruption_type: str
    suggested_disruption_subtype: str | None
    suggested_event_ref: str | None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    created_at: datetime

    class Config:
        from_attributes = True


class ClassificationDecisionIn(BaseModel):
    """Classification decision request schema."""

    reviewer_decision: str = Field(
        ..., description="Reviewer action: confirm, revise, or reject"
    )
    final_disruption_type: str | None = Field(
        None, description="Final disruption type (required for revise)"
    )
    final_disruption_subtype: str | None = Field(
        None, description="Final disruption subtype (optional override)"
    )
    final_event_ref: str | None = Field(
        None, description="Final event reference (optional override)"
    )
    reviewer_comment: str | None = Field(
        None, description="Reviewer comment or rejection reason"
    )


class ClassificationDecisionOut(BaseModel):
    """Classification decision response schema."""

    id: str
    intake_case_id: str
    suggested_disruption_type: str
    suggested_disruption_subtype: str | None
    suggested_event_ref: str | None
    confidence_score: float
    reviewer_decision: str
    final_disruption_type: str | None
    final_disruption_subtype: str | None
    final_event_ref: str | None
    reviewer_comment: str | None
    decided_by_user_id: str
    decided_at_utc: datetime
    created_at: datetime

    class Config:
        from_attributes = True
