"""Classification router for AI-assisted recommendation and human-gated decision."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.classification_schemas import (
    ClassificationDecisionIn,
    ClassificationDecisionOut,
    ClassificationRecommendationOut,
)
from app.services.classification_service import ClassificationService

router = APIRouter(prefix="/api/v1/classification", tags=["classification"])


@router.post("/cases/{case_id}/recommendation", response_model=ClassificationRecommendationOut)
def generate_classification_recommendation(
    case_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate AI-assisted classification recommendation.
    
    FR-003: Classify intake against correct disruption event.
    - AGN1 generates recommendation with confidence score
    - Presents recommendation for human review
    - No binding decision without explicit human action (BR-06)
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    service = ClassificationService(db, correlation_id)
    
    try:
        return service.generate_recommendation(case_id, actor_id=str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/cases/{case_id}/decision", response_model=ClassificationDecisionOut)
def record_classification_decision(
    case_id: str,
    decision: ClassificationDecisionIn,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record reviewer classification decision.
    
    FR-003: Human-gated classification decision with BR-06 AMBER gate.
    - Requires Event Approval Reviewer role (403 if unauthorized)
    - Reviewer can confirm, revise, or reject recommendation
    - Decision recorded with audit trail
    - No binding without explicit human action
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    service = ClassificationService(db, correlation_id)
    
    try:
        return service.record_decision(
            case_id, decision, user_id=str(current_user.id), user_role=current_user.role
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
