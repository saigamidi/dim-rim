"""Unit tests for audit service."""
import uuid
from datetime import datetime, timezone

from app.models.intake_case import IntakeCase
from app.services.audit_service import AuditService


def test_record_event_creates_audit_record(db_session):
    """Test that record_event creates audit record."""
    # Create test case first (audit events have FK to intake_case)
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="AUDIT-TEST-001",
        source_email_id=f"audit-{uuid.uuid4()}",
        source_address="test@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    service = AuditService(db_session)
    
    correlation_id = str(uuid.uuid4())
    
    result = service.record_event(
        intake_case_id=case_id,
        correlation_id=correlation_id,
        actor_type="user",
        actor_id="test-user-1",
        action_type="test_action",
        entity_type="test_entity",
        entity_id="entity-1",
        outcome="success",
        metadata={"key": "value"},
    )
    
    assert result.id is not None
    assert result.intake_case_id == case_id
    assert result.correlation_id == correlation_id
    assert result.actor_type == "user"
    assert result.action_type == "test_action"
    assert result.outcome == "success"


def test_get_case_events_returns_events_in_order(db_session):
    """Test that get_case_events returns events ordered by occurrence time."""
    # Create test case first
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="AUDIT-TEST-002",
        source_email_id=f"audit-{uuid.uuid4()}",
        source_address="test@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    service = AuditService(db_session)
    
    correlation_id = str(uuid.uuid4())
    
    # Create multiple events
    service.record_event(
        intake_case_id=case_id,
        correlation_id=correlation_id,
        actor_type="user",
        actor_id="user-1",
        action_type="action_1",
        entity_type="entity",
        entity_id="1",
        outcome="success",
        metadata={},
    )
    
    service.record_event(
        intake_case_id=case_id,
        correlation_id=correlation_id,
        actor_type="user",
        actor_id="user-2",
        action_type="action_2",
        entity_type="entity",
        entity_id="2",
        outcome="success",
        metadata={},
    )
    
    events = service.get_case_events(case_id)
    
    assert len(events) == 2
    assert events[0].action_type == "action_1"
    assert events[1].action_type == "action_2"
    # Verify chronological order
    assert events[0].occurred_at_utc <= events[1].occurred_at_utc


def test_get_correlation_events_returns_all_events_for_correlation(db_session):
    """Test that get_correlation_events returns all events for correlation ID."""
    # Create test case first
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="AUDIT-TEST-003",
        source_email_id=f"audit-{uuid.uuid4()}",
        source_address="test@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    service = AuditService(db_session)
    
    correlation_id = str(uuid.uuid4())
    
    # Create events with same correlation ID
    service.record_event(
        intake_case_id=case_id,
        correlation_id=correlation_id,
        actor_type="user",
        actor_id="user-1",
        action_type="action_1",
        entity_type="entity",
        entity_id="1",
        outcome="success",
        metadata={},
    )
    
    service.record_event(
        intake_case_id=case_id,
        correlation_id=correlation_id,
        actor_type="system",
        actor_id="system",
        action_type="action_2",
        entity_type="entity",
        entity_id="2",
        outcome="success",
        metadata={},
    )
    
    events = service.get_correlation_events(correlation_id)
    
    assert len(events) == 2
    assert all(e.correlation_id == correlation_id for e in events)


def test_get_case_events_returns_empty_for_nonexistent_case(db_session):
    """Test that get_case_events returns empty list for nonexistent case."""
    service = AuditService(db_session)
    
    events = service.get_case_events("nonexistent-case-id")
    
    assert events == []
