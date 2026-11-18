"""Integration tests for classification module."""
import uuid
from datetime import datetime, timezone

from app.models.classification_decision import ClassificationDecision
from app.models.intake_case import IntakeCase
from app.repositories.classification_decision_repository import (
    ClassificationDecisionRepository,
)
from app.services.classification_service import ClassificationService


def test_classification_service_with_real_repository(db_session):
    """Test classification service with real repository and database."""
    # Create test case
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CLASS-INT-001",
        source_email_id=f"class-test-{uuid.uuid4()}",
        source_address="class@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Classification Integration Test",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    correlation_id = str(uuid.uuid4())
    service = ClassificationService(db_session, correlation_id)
    
    # Generate recommendation
    recommendation = service.generate_recommendation(case_id, actor_id="AGN1")
    
    # Verify via repository
    repo = ClassificationDecisionRepository(db_session)
    decision = repo.get_by_id(recommendation.id)
    
    assert decision is not None
    assert decision.intake_case_id == case_id
    assert decision.reviewer_decision == "pending"


def test_classification_decision_repository_crud(db_session):
    """Test classification decision repository CRUD operations."""
    # Create test case first
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="CLASS-REPO-001",
        source_email_id=f"repo-class-{uuid.uuid4()}",
        source_address="repo@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Repository Test",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    repo = ClassificationDecisionRepository(db_session)
    
    decision_id = str(uuid.uuid4())
    decision = ClassificationDecision(
        id=decision_id,
        intake_case_id=case_id,
        suggested_disruption_type="Test Type",
        suggested_disruption_subtype=None,
        suggested_event_ref=None,
        confidence_score=0.90,
        reviewer_decision="pending",
        final_disruption_type=None,
        final_disruption_subtype=None,
        final_event_ref=None,
        reviewer_comment=None,
        decided_by_user_id="AGN1",
        decided_at_utc=datetime.now(timezone.utc),
    )
    
    # Create
    created = repo.create(decision)
    assert created.id == decision_id
    
    # Read by ID
    retrieved = repo.get_by_id(decision_id)
    assert retrieved is not None
    assert retrieved.suggested_disruption_type == "Test Type"
    
    # Read by case ID
    by_case = repo.get_by_case_id(case_id)
    assert by_case is not None
    assert by_case.id == decision_id
