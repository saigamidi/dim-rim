"""Unit tests for classification service."""
import uuid
from datetime import datetime, timezone

import pytest

from app.models.intake_case import IntakeCase
from app.services.classification_service import ClassificationService


def test_generate_recommendation_creates_pending_decision(db_session):
    """Test that generating recommendation creates pending decision."""
    # Create test case
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CASE-TEST-001",
        source_email_id="test-email",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Disruption Alert",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    result = service.generate_recommendation(case_id, actor_id="AGN1")
    
    assert result.id is not None
    assert result.intake_case_id == case_id
    assert result.suggested_disruption_type == "Production Disruption"
    assert result.confidence_score == 0.87
    
    # Verify case status updated
    db_session.refresh(case)
    assert case.intake_status == "classification_pending_review"


def test_generate_recommendation_raises_error_for_nonexistent_case(db_session):
    """Test that generating recommendation for nonexistent case raises error."""
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    with pytest.raises(ValueError, match="Intake case not found"):
        service.generate_recommendation("nonexistent-id", actor_id="AGN1")


def test_record_decision_confirm_accepts_recommendation(db_session):
    """Test that confirm decision accepts AGN1 recommendation."""
    # Create test case and pending recommendation
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CASE-TEST-002",
        source_email_id="test-email-2",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Issue",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    # Generate recommendation
    recommendation = service.generate_recommendation(case_id, actor_id="AGN1")
    
    # Import here to avoid circular dependency at module level
    from app.schemas.classification_schemas import ClassificationDecisionIn
    
    # Confirm decision
    decision_in = ClassificationDecisionIn(
        reviewer_decision="confirm",
        reviewer_comment="Looks correct",
    )
    
    result = service.record_decision(
        case_id, decision_in, user_id=1, user_role="Event Approval Reviewer"
    )
    
    assert result.reviewer_decision == "confirm"
    assert result.final_disruption_type == recommendation.suggested_disruption_type
    assert result.decided_by_user_id == "1"
    
    # Verify case status updated
    db_session.refresh(case)
    assert case.intake_status == "classification_decided"


def test_record_decision_revise_overrides_recommendation(db_session):
    """Test that revise decision overrides AGN1 recommendation."""
    # Create test case and pending recommendation
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CASE-TEST-003",
        source_email_id="test-email-3",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Supply Chain Issue",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    # Generate recommendation
    service.generate_recommendation(case_id, actor_id="AGN1")
    
    from app.schemas.classification_schemas import ClassificationDecisionIn
    
    # Revise decision
    decision_in = ClassificationDecisionIn(
        reviewer_decision="revise",
        final_disruption_type="Logistics Disruption",
        final_disruption_subtype="Shipping Delay",
        reviewer_comment="Actually a logistics issue",
    )
    
    result = service.record_decision(
        case_id, decision_in, user_id=1, user_role="Event Approval Reviewer"
    )
    
    assert result.reviewer_decision == "revise"
    assert result.final_disruption_type == "Logistics Disruption"
    assert result.final_disruption_subtype == "Shipping Delay"


def test_record_decision_reject_clears_binding(db_session):
    """Test that reject decision clears binding."""
    # Create test case and pending recommendation
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CASE-TEST-004",
        source_email_id="test-email-4",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Unclear Issue",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    # Generate recommendation
    service.generate_recommendation(case_id, actor_id="AGN1")
    
    from app.schemas.classification_schemas import ClassificationDecisionIn
    
    # Reject decision
    decision_in = ClassificationDecisionIn(
        reviewer_decision="reject",
        reviewer_comment="Not enough information",
    )
    
    result = service.record_decision(
        case_id, decision_in, user_id=1, user_role="Event Approval Reviewer"
    )
    
    assert result.reviewer_decision == "reject"
    assert result.final_disruption_type is None
    assert result.final_disruption_subtype is None
    assert result.final_event_ref is None


def test_record_decision_requires_event_approval_reviewer_role(db_session):
    """Test BR-06 AMBER gate: requires Event Approval Reviewer role."""
    # Create test case and pending recommendation
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CASE-TEST-005",
        source_email_id="test-email-5",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test Issue",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    # Generate recommendation
    service.generate_recommendation(case_id, actor_id="AGN1")
    
    from app.schemas.classification_schemas import ClassificationDecisionIn
    
    decision_in = ClassificationDecisionIn(
        reviewer_decision="confirm",
    )
    
    # Try with wrong role
    with pytest.raises(PermissionError, match="not authorized"):
        service.record_decision(
            case_id, decision_in, user_id=1, user_role="Disruption Manager"
        )


def test_record_decision_revise_requires_final_disruption_type(db_session):
    """Test that revise decision requires final_disruption_type."""
    # Create test case and pending recommendation
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CASE-TEST-006",
        source_email_id="test-email-6",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test Issue",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    # Generate recommendation
    service.generate_recommendation(case_id, actor_id="AGN1")
    
    from app.schemas.classification_schemas import ClassificationDecisionIn
    
    decision_in = ClassificationDecisionIn(
        reviewer_decision="revise",
        # Missing final_disruption_type
    )
    
    with pytest.raises(ValueError, match="final_disruption_type required"):
        service.record_decision(
            case_id, decision_in, user_id=1, user_role="Event Approval Reviewer"
        )
