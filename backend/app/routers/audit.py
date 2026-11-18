"""Audit router for case event retrieval."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.audit_schemas import AuditEventOut
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/cases/{case_id}/events", response_model=list[AuditEventOut])
def get_case_audit_events(
    case_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List case audit events.
    
    Returns all audit events for a case, ordered by occurrence time.
    Supports append-only audit trail for FR-001 through FR-005 continuity.
    """
    service = AuditService(db)
    
    return service.get_case_events(case_id)
