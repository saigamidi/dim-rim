"""Unit tests for inbox submission service."""
import uuid
from datetime import datetime, timezone

import pytest

from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.services.inbox_submission_service import InboxSubmissionService
from app.schemas.intake_schemas import InboxSubmissionIn


def test_submit_inbox_email_creates_case(db_session):
    """Test that submitting an inbox email creates an intake case."""
    correlation_id = str(uuid.uuid4())
    service = InboxSubmissionService(db_session, correlation_id)
    
    submission = InboxSubmissionIn(
        source_email_id="test-email-001",
        source_address="supplier@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Disruption - VIN List Attached",
        has_attachments=True,
    )
    
    result = service.submit_inbox_email(submission, actor_id="test-user-1")
    
    assert result.id is not None
    assert result.case_key.startswith("CASE-")
    assert result.source_email_id == "test-email-001"
    assert result.intake_status == "received"
    assert result.correlation_id == correlation_id
    
    # Verify case exists in database
    case = db_session.query(IntakeCase).filter(IntakeCase.id == result.id).first()
    assert case is not None
    assert case.source_address == "supplier@example.com"


def test_submit_inbox_email_creates_attachment_placeholder(db_session):
    """Test that submitting with attachments creates placeholder."""
    correlation_id = str(uuid.uuid4())
    service = InboxSubmissionService(db_session, correlation_id)
    
    submission = InboxSubmissionIn(
        source_email_id="test-email-002",
        source_address="supplier@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Disruption",
        has_attachments=True,
    )
    
    result = service.submit_inbox_email(submission, actor_id="test-user-1")
    
    # Verify attachment placeholder created
    attachments = (
        db_session.query(EmailAttachment)
        .filter(EmailAttachment.intake_case_id == result.id)
        .all()
    )
    assert len(attachments) == 1
    assert attachments[0].parse_status == "pending"


def test_submit_duplicate_email_returns_existing_case(db_session):
    """Test that submitting duplicate email returns existing case."""
    correlation_id = str(uuid.uuid4())
    service = InboxSubmissionService(db_session, correlation_id)
    
    submission = InboxSubmissionIn(
        source_email_id="duplicate-email",
        source_address="supplier@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Disruption",
        has_attachments=False,
    )
    
    # First submission
    first = service.submit_inbox_email(submission, actor_id="test-user-1")
    
    # Second submission with same source_email_id
    second = service.submit_inbox_email(submission, actor_id="test-user-1")
    
    assert first.id == second.id
    assert first.case_key == second.case_key


def test_submit_non_candidate_raises_error(db_session):
    """Test that non-disruption candidate raises error."""
    correlation_id = str(uuid.uuid4())
    service = InboxSubmissionService(db_session, correlation_id)
    
    submission = InboxSubmissionIn(
        source_email_id="non-candidate-email",
        source_address="info@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Meeting reminder for next week",
        has_attachments=False,
    )
    
    with pytest.raises(ValueError, match="not a disruption candidate"):
        service.submit_inbox_email(submission, actor_id="test-user-1")


def test_get_case_returns_case(db_session):
    """Test that get_case returns case by ID."""
    correlation_id = str(uuid.uuid4())
    service = InboxSubmissionService(db_session, correlation_id)
    
    submission = InboxSubmissionIn(
        source_email_id="test-email-003",
        source_address="supplier@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Disruption",
        has_attachments=False,
    )
    
    created = service.submit_inbox_email(submission, actor_id="test-user-1")
    
    retrieved = service.get_case(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.case_key == created.case_key


def test_get_case_returns_none_for_nonexistent(db_session):
    """Test that get_case returns None for nonexistent case."""
    correlation_id = str(uuid.uuid4())
    service = InboxSubmissionService(db_session, correlation_id)
    
    result = service.get_case("nonexistent-id")
    
    assert result is None
