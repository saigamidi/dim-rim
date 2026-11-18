"""Parsing router for attachment parsing endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.middleware.correlation_middleware import get_correlation_id
from app.models.user import User
from app.schemas.parsing_schemas import (
    AttachmentParseRequest,
    AttachmentParseResultOut,
    CandidateRowOut,
)
from app.services.attachment_parsing_service import AttachmentParsingService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/parsing", tags=["parsing"])


@router.post("/attachments/{attachment_id}/parse", response_model=AttachmentParseResultOut)
def parse_attachment(
    attachment_id: str,
    parse_request: AttachmentParseRequest = AttachmentParseRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AttachmentParseResultOut:
    """
    Parse an attachment into canonical candidate rows.
    
    Orchestrates TOL2 seam, normalizes rows, persists with row-level lineage.
    Handles parse failures explicitly. Idempotent via force_reparse flag.
    
    **x-requirement:** [FR-002]
    """
    correlation_id = get_correlation_id()
    
    logger.info(
        f"Parse attachment request: attachment_id={attachment_id}, "
        f"force_reparse={parse_request.force_reparse}, user={current_user.email}, "
        f"correlation_id={correlation_id}"
    )

    parsing_service = AttachmentParsingService(db)
    audit_service = AuditService(db)

    try:
        # Parse attachment
        result = parsing_service.parse_attachment(
            attachment_id=attachment_id,
            force_reparse=parse_request.force_reparse,
        )

        # Record audit event
        # Get case_id from attachment (result contains lineage_base_ref)
        case_id = result.lineage_base_ref.split("/")[0].replace("lin-", "")
        
        audit_service.record_event(
            intake_case_id=case_id,
            correlation_id=correlation_id,
            actor_type="user",
            actor_id=current_user.email,
            action_type="attachment_parsed",
            entity_type="email_attachment",
            entity_id=attachment_id,
            outcome="success" if result.parse_status == "parsed" else "partial",
            metadata={
                "row_count": result.row_count,
                "failure_count": result.failure_count,
                "force_reparse": parse_request.force_reparse,
            },
        )

        db.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse attachment failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Parse attachment failed: {str(e)}")


@router.get("/cases/{case_id}/rows", response_model=list[CandidateRowOut])
def get_case_candidate_rows(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CandidateRowOut]:
    """
    Get all candidate rows for a case.
    
    Returns paginated canonical rows with source_row_number, canonical_vin_candidate,
    row_status, and lineage metadata.
    
    **x-requirement:** [FR-002]
    """
    correlation_id = get_correlation_id()
    
    logger.info(
        f"Get candidate rows request: case_id={case_id}, user={current_user.email}, "
        f"correlation_id={correlation_id}"
    )

    parsing_service = AttachmentParsingService(db)

    try:
        rows = parsing_service.get_candidate_rows_by_case(case_id)
        return rows

    except Exception as e:
        logger.error(f"Get candidate rows failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get candidate rows failed: {str(e)}")
