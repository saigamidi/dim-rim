"""Classification service with AGN1 recommendation logic and human-gated decision flow."""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.classification_decision import ClassificationDecision
from app.repositories.classification_decision_repository import (
    ClassificationDecisionRepository,
)
from app.repositories.intake_case_repository import IntakeCaseRepository
from app.schemas.classification_schemas import (
    ClassificationDecisionIn,
    ClassificationDecisionOut,
    ClassificationRecommendationOut,
)
from app.services.audit_service import AuditService


class ClassificationService:
    """Service for classification recommendation and human-gated decision flow.
    
    AGN1 Classification Logic:
    - Generate AI-assisted recommendation with confidence score
    - Present recommendation for human review
    - Human actions: confirm, revise, or reject
    - BR-06 AMBER gate: no binding without explicit human action
    """

    def __init__(self, session: Session, correlation_id: str):
        self.session = session
        self.correlation_id = correlation_id
        self.decision_repo = ClassificationDecisionRepository(session)
        self.intake_repo = IntakeCaseRepository(session)
        self.audit_service = AuditService(session)

    def generate_recommendation(
        self, case_id: str, actor_id: str
    ) -> ClassificationRecommendationOut:
        """Generate AI-assisted classification recommendation.
        
        AGN1 orchestration:
        - Analyze case metadata and attachments
        - Generate disruption type/subtype recommendation
        - Calculate confidence score
        - Create pending decision record
        """
        # Verify case exists
        case = self.intake_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Intake case not found: {case_id}")
        
        # AGN1: Generate AI-assisted recommendation (mocked for MVP)
        # Future: Will integrate with actual ML model or rule engine
        suggested_type = self._infer_disruption_type(case.subject)
        confidence = 0.87  # Mocked confidence score
        
        # Check for existing pending decision
        existing = self.decision_repo.get_by_case_id(case_id)
        if existing and existing.reviewer_decision == "pending":
            return ClassificationRecommendationOut.model_validate(existing)
        
        # Create pending classification decision
        decision_id = str(uuid.uuid4())
        decision = ClassificationDecision(
            id=decision_id,
            intake_case_id=case_id,
            suggested_disruption_type=suggested_type,
            suggested_disruption_subtype=None,
            suggested_event_ref=None,
            confidence_score=confidence,
            reviewer_decision="pending",
            final_disruption_type=None,
            final_disruption_subtype=None,
            final_event_ref=None,
            reviewer_comment=None,
            decided_by_user_id="AGN1",
            decided_at_utc=datetime.now(timezone.utc),
        )
        
        created = self.decision_repo.create(decision)
        
        # Update case status to classification_pending_review
        self.intake_repo.update_status(case_id, "classification_pending_review")
        
        # Record audit event
        self.audit_service.record_event(
            intake_case_id=case_id,
            correlation_id=self.correlation_id,
            actor_type="system",
            actor_id="AGN1",
            action_type="classification_recommendation",
            entity_type="classification_decision",
            entity_id=decision_id,
            outcome="success",
            metadata={
                "suggested_disruption_type": suggested_type,
                "confidence_score": confidence,
            },
        )
        
        return ClassificationRecommendationOut.model_validate(created)

    def record_decision(
        self, case_id: str, decision_in: ClassificationDecisionIn, user_id: str, user_role: str
    ) -> ClassificationDecisionOut:
        """Record human classification decision with BR-06 AMBER gate.
        
        BR-06 AMBER gate: Event Approval Reviewer role required.
        Human actions:
        - confirm: Accept AGN1 recommendation
        - revise: Override with different type/subtype/event
        - reject: Clear binding, preserve history
        """
        # BR-06 AMBER gate: Check role authorization
        if user_role != "Event Approval Reviewer":
            raise PermissionError(
                f"Role '{user_role}' not authorized for classification decisions. "
                "Requires: Event Approval Reviewer"
            )
        
        # Verify case and pending recommendation exist
        case = self.intake_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Intake case not found: {case_id}")
        
        pending = self.decision_repo.get_by_case_id(case_id)
        if not pending or pending.reviewer_decision != "pending":
            raise ValueError(f"No pending recommendation for case: {case_id}")
        
        # Validate decision input
        if decision_in.reviewer_decision not in ["confirm", "revise", "reject"]:
            raise ValueError(
                f"Invalid reviewer_decision: {decision_in.reviewer_decision}. "
                "Must be: confirm, revise, or reject"
            )
        
        if decision_in.reviewer_decision == "revise":
            if not decision_in.final_disruption_type:
                raise ValueError("final_disruption_type required for revise decision")
        
        # Update decision record
        pending.reviewer_decision = decision_in.reviewer_decision
        pending.decided_by_user_id = str(user_id)
        pending.decided_at_utc = datetime.now(timezone.utc)
        pending.reviewer_comment = decision_in.reviewer_comment
        
        if decision_in.reviewer_decision == "confirm":
            # Accept AGN1 recommendation
            pending.final_disruption_type = pending.suggested_disruption_type
            pending.final_disruption_subtype = pending.suggested_disruption_subtype
            pending.final_event_ref = pending.suggested_event_ref
        elif decision_in.reviewer_decision == "revise":
            # Override with reviewer values
            pending.final_disruption_type = decision_in.final_disruption_type
            pending.final_disruption_subtype = decision_in.final_disruption_subtype
            pending.final_event_ref = decision_in.final_event_ref
        else:  # reject
            # Clear binding
            pending.final_disruption_type = None
            pending.final_disruption_subtype = None
            pending.final_event_ref = None
        
        self.session.commit()
        self.session.refresh(pending)
        
        # Update case status
        self.intake_repo.update_status(case_id, "classification_decided")
        
        # Record audit event
        self.audit_service.record_event(
            intake_case_id=case_id,
            correlation_id=self.correlation_id,
            actor_type="user",
            actor_id=str(user_id),
            action_type="classification_decision",
            entity_type="classification_decision",
            entity_id=pending.id,
            outcome=decision_in.reviewer_decision,
            metadata={
                "reviewer_decision": decision_in.reviewer_decision,
                "final_disruption_type": pending.final_disruption_type,
                "reviewer_comment": decision_in.reviewer_comment,
                "user_role": user_role,
            },
        )
        
        return ClassificationDecisionOut.model_validate(pending)

    def _infer_disruption_type(self, subject: str) -> str:
        """Infer disruption type from email subject (mocked AGN1 logic).
        
        Future: Will be replaced with actual ML model or rule engine.
        """
        subject_lower = subject.lower()
        if "production" in subject_lower:
            return "Production Disruption"
        elif "supply" in subject_lower or "supplier" in subject_lower:
            return "Supply Chain Disruption"
        elif "logistics" in subject_lower or "shipping" in subject_lower:
            return "Logistics Disruption"
        else:
            return "General Disruption"
