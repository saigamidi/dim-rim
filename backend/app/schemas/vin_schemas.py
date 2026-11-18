"""VIN domain schemas for extraction and summary."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VinExtractionRunOut(BaseModel):
    """Response schema for VIN extraction operation."""

    case_id: str
    extracted_count: int
    deduplicated_count: int
    rejected_empty_count: int
    run_status: str

    model_config = ConfigDict(from_attributes=True)


class VinRecordOut(BaseModel):
    """Response schema for VIN record."""

    id: str
    intake_case_id: str
    candidate_row_id: str
    raw_vin: str | None
    normalized_vin: str | None
    extraction_status: str
    is_duplicate_within_case: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VinExtractionSummaryOut(BaseModel):
    """Response schema for VIN extraction summary (counts only)."""

    case_id: str
    extracted: int
    deduplicated: int
    rejected: int


class VinValidationResultOut(BaseModel):
    """Response schema for VIN validation result."""

    id: str
    vin_record_id: str
    validation_status: str
    failure_reason_code: str | None
    failure_reason_detail: str | None
    checksum_passed: bool
    validated_at_utc: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VinValidationRunOut(BaseModel):
    """Response schema for VIN validation operation."""

    case_id: str
    valid_count: int
    invalid_count: int
    failure_breakdown: dict[str, int]
    validated_at_utc: datetime


class VinValidationSummaryOut(BaseModel):
    """Response schema for full VIN summary including validation."""

    case_id: str
    extracted: int
    deduplicated: int
    rejected: int
    valid: int
    invalid: int
    failure_reason_breakdown: dict[str, int]
