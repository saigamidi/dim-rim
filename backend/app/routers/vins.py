"""VINs router for VIN extraction and summary endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.middleware.correlation_middleware import get_correlation_id
from app.models.user import User
from app.schemas.vin_schemas import (
    VinExtractionRunOut,
    VinValidationRunOut,
    VinValidationSummaryOut,
)
from app.services.audit_service import AuditService
from app.services.vin_processing_service import VinProcessingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vins", tags=["vins"])


@router.post("/cases/{case_id}/extract", response_model=VinExtractionRunOut)
def extract_vins(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VinExtractionRunOut:
    """
    Extract VINs from candidate rows.
    
    Normalizes (uppercase, trim whitespace), deduplicates within case
    (first occurrence kept, lineage preserved), produces counts.
    Idempotent rerun allowed.
    
    **x-requirement:** [FR-004]
    """
    correlation_id = get_correlation_id()
    
    logger.info(
        f"Extract VINs request: case_id={case_id}, user={current_user.email}, "
        f"correlation_id={correlation_id}"
    )

    vin_service = VinProcessingService(db)
    audit_service = AuditService(db)

    try:
        # Extract VINs
        result = vin_service.extract_vins(case_id)

        # Record audit event
        audit_service.record_event(
            intake_case_id=case_id,
            correlation_id=correlation_id,
            actor_type="user",
            actor_id=current_user.email,
            action_type="vins_extracted",
            entity_type="intake_case",
            entity_id=case_id,
            outcome="success",
            metadata={
                "extracted_count": result.extracted_count,
                "deduplicated_count": result.deduplicated_count,
                "rejected_empty_count": result.rejected_empty_count,
            },
        )

        db.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extract VINs failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Extract VINs failed: {str(e)}")


@router.post("/cases/{case_id}/validate", response_model=VinValidationRunOut)
def validate_vins(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VinValidationRunOut:
    """
    Run BR-01 deterministic validation on extracted VINs.
    
    Validates length, character validity, and checksum rules.
    Persists explicit failure reason codes (wrong_length, invalid_character,
    checksum_failure, empty_value). Invalid VINs blocked from future
    lookup/load paths. Idempotent rerun allowed.
    
    **x-requirement:** [FR-005]
    """
    correlation_id = get_correlation_id()
    
    logger.info(
        f"Validate VINs request: case_id={case_id}, user={current_user.email}, "
        f"correlation_id={correlation_id}"
    )

    vin_service = VinProcessingService(db)
    audit_service = AuditService(db)

    try:
        # Validate VINs
        result = vin_service.validate_vins(case_id)

        # Record audit event
        audit_service.record_event(
            intake_case_id=case_id,
            correlation_id=correlation_id,
            actor_type="user",
            actor_id=current_user.email,
            action_type="vins_validated",
            entity_type="intake_case",
            entity_id=case_id,
            outcome="success",
            metadata={
                "valid_count": result.valid_count,
                "invalid_count": result.invalid_count,
                "failure_breakdown": result.failure_breakdown,
            },
        )

        db.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validate VINs failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Validate VINs failed: {str(e)}")


@router.get("/cases/{case_id}/summary", response_model=VinValidationSummaryOut)
def get_vin_summary(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VinValidationSummaryOut:
    """
    Get full VIN summary including extraction and validation counts.
    
    Returns extraction counts (extracted, deduplicated, rejected) and
    validation counts (valid, invalid, failure_reason_breakdown).
    
    **x-requirement:** [FR-004, FR-005]
    """
    correlation_id = get_correlation_id()
    
    logger.info(
        f"Get VIN summary request: case_id={case_id}, user={current_user.email}, "
        f"correlation_id={correlation_id}"
    )

    vin_service = VinProcessingService(db)

    try:
        summary = vin_service.get_validation_summary(case_id)
        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get VIN summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get VIN summary failed: {str(e)}")


@router.get("/cases/{case_id}/records")
def get_vin_records(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all VIN records for a case with validation results.
    
    Returns list of VIN records including extraction status and validation results.
    
    **x-requirement:** [FR-004, FR-005]
    """
    correlation_id = get_correlation_id()
    
    logger.info(
        f"Get VIN records request: case_id={case_id}, user={current_user.email}, "
        f"correlation_id={correlation_id}"
    )

    vin_service = VinProcessingService(db)

    try:
        return vin_service.get_vin_records_with_validation(case_id)
    except Exception as e:
        logger.error(f"Get VIN records failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get VIN records failed: {str(e)}")
