"""Integration tests for intake module (service + repository + database)."""
import uuid
from datetime import datetime, timezone

from app.models.intake_case import IntakeCase
from app.repositories.intake_case_repository import IntakeCaseRepository
from app.services.inbox_submission_service import InboxSubmissionService
from app.schemas.intake_schemas import InboxSubmissionIn


def test_intake_service_with_real_repository(db_session):
    """Test intake service with real repository and database."""
    correlation_id = str(uuid.uuid4())
    service = InboxSubmissionService(db_session, correlation_id)
    
    submission = InboxSubmissionIn(
        source_email_id=f"int-test-{uuid.uuid4()}",
        source_address="integration@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Integration Test Disruption",
        has_attachments=True,
    )
    
    result = service.submit_inbox_email(submission, actor_id="test-user")
    
    # Verify via repository
    repo = IntakeCaseRepository(db_session)
    case = repo.get_by_id(result.id)
    
    assert case is not None
    assert case.id == result.id
    assert case.source_email_id == submission.source_email_id
    assert len(case.attachments) == 1


def test_intake_case_repository_crud(db_session):
    """Test intake case repository CRUD operations."""
    repo = IntakeCaseRepository(db_session)
    
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="INT-TEST-001",
        source_email_id=f"repo-test-{uuid.uuid4()}",
        source_address="repo@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Repository Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    
    # Create
    created = repo.create(case)
    assert created.id == case_id
    
    # Read
    retrieved = repo.get_by_id(case_id)
    assert retrieved is not None
    assert retrieved.case_key == "INT-TEST-001"
    
    # Update status
    updated = repo.update_status(case_id, "parsed")
    assert updated.intake_status == "parsed"
