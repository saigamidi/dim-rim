"""Acceptance tests for audit endpoints."""
import uuid
from datetime import datetime, timezone

from app.models.audit_event import AuditEvent
from app.models.intake_case import IntakeCase


def test_get_case_audit_events_returns_events(auth_client, db_session):
    """Test GET /api/v1/audit/cases/{case_id}/events returns events."""
    # Create test case
    case_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="AUDIT-ACC-001",
        source_email_id=f"audit-{uuid.uuid4()}",
        source_address="audit@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Audit Test",
        intake_status="received",
        correlation_id=correlation_id,
    )
    db_session.add(case)
    db_session.commit()
    
    # Create audit events
    event1 = AuditEvent(
        intake_case_id=case_id,
        correlation_id=correlation_id,
        actor_type="system",
        actor_id="test",
        action_type="test_action_1",
        entity_type="intake_case",
        entity_id=case_id,
        outcome="success",
        metadata_json='{"test": "data"}',
        occurred_at_utc=datetime.now(timezone.utc),
    )
    event2 = AuditEvent(
        intake_case_id=case_id,
        correlation_id=correlation_id,
        actor_type="user",
        actor_id="user-1",
        action_type="test_action_2",
        entity_type="intake_case",
        entity_id=case_id,
        outcome="success",
        metadata_json='{"test": "data2"}',
        occurred_at_utc=datetime.now(timezone.utc),
    )
    db_session.add(event1)
    db_session.add(event2)
    db_session.commit()
    
    response = auth_client.get(f"/api/v1/audit/cases/{case_id}/events")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert data[0]["intake_case_id"] == case_id
    assert data[0]["correlation_id"] == correlation_id


def test_get_case_audit_events_empty_returns_empty_list(auth_client):
    """Test GET audit events for case with no events returns empty list."""
    response = auth_client.get(f"/api/v1/audit/cases/{uuid.uuid4()}/events")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_audit_events_requires_auth(client, db_session):
    """Test GET audit events requires authentication."""
    case_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/audit/cases/{case_id}/events")
    
    assert response.status_code == 401  # HTTPBearer returns 401 without credentials
