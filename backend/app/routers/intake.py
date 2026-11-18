"""Intake router for disruption case submission and retrieval."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.intake_schemas import InboxSubmissionIn, IntakeCaseOut
from app.services.inbox_submission_service import InboxSubmissionService

router = APIRouter(prefix="/api/v1/intake", tags=["intake"])


@router.post("/submissions", response_model=IntakeCaseOut, status_code=status.HTTP_201_CREATED)
def submit_inbox_email(
    submission: InboxSubmissionIn,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Register disruption inbox submission.
    
    FR-001: Receive disruption-related inbox submissions.
    - Records receipt metadata (source, timestamp, subject, attachment presence)
    - Distinguishes disruption candidates from non-cases
    - Creates intake case record for human review
    - Produces audit record linked to case
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    service = InboxSubmissionService(db, correlation_id)
    
    try:
        return service.submit_inbox_email(submission, actor_id=str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/cases/{case_id}", response_model=IntakeCaseOut)
def get_intake_case(
    case_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Read intake case summary.
    
    Returns intake case with attachments and current status.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown") if request else "unknown"
    service = InboxSubmissionService(db, correlation_id)
    
    case = service.get_case(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intake case not found: {case_id}",
        )
    
    return case
