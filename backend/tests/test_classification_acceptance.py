"""Acceptance tests for classification endpoints."""
import uuid
from datetime import datetime, timezone

from app.models.intake_case import IntakeCase


def test_post_recommendation_generates_classification(auth_client, db_session):
    """Test POST /api/v1/classification/cases/{case_id}/recommendation."""
    # Create test case
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="ACC-CLASS-001",
        source_email_id=f"class-acc-{uuid.uuid4()}",
        source_address="class@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Disruption Test",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    response = auth_client.post(f"/api/v1/classification/cases/{case_id}/recommendation")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["intake_case_id"] == case_id
    assert data["suggested_disruption_type"] is not None
    assert 0 <= data["confidence_score"] <= 1


def test_post_decision_confirm_accepts_recommendation(auth_client, db_session):
    """Test POST /api/v1/classification/cases/{case_id}/decision with confirm."""
    # Create test case
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="ACC-DEC-001",
        source_email_id=f"dec-acc-{uuid.uuid4()}",
        source_address="dec@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Production Disruption",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    # Generate recommendation first
    auth_client.post(f"/api/v1/classification/cases/{case_id}/recommendation")
    
    # Record confirm decision
    response = auth_client.post(
        f"/api/v1/classification/cases/{case_id}/decision",
        json={
            "reviewer_decision": "confirm",
            "reviewer_comment": "Looks good",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["reviewer_decision"] == "confirm"
    assert data["final_disruption_type"] is not None
    assert data["decided_by_user_id"] is not None


def test_post_decision_revise_overrides_recommendation(auth_client, db_session):
    """Test POST /api/v1/classification/cases/{case_id}/decision with revise."""
    # Create test case
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="ACC-REV-001",
        source_email_id=f"rev-acc-{uuid.uuid4()}",
        source_address="rev@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test Issue",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    # Generate recommendation
    auth_client.post(f"/api/v1/classification/cases/{case_id}/recommendation")
    
    # Record revise decision
    response = auth_client.post(
        f"/api/v1/classification/cases/{case_id}/decision",
        json={
            "reviewer_decision": "revise",
            "final_disruption_type": "Logistics Disruption",
            "final_disruption_subtype": "Shipping",
            "reviewer_comment": "Actually logistics",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["reviewer_decision"] == "revise"
    assert data["final_disruption_type"] == "Logistics Disruption"
    assert data["final_disruption_subtype"] == "Shipping"


def test_post_decision_reject_clears_binding(auth_client, db_session):
    """Test POST /api/v1/classification/cases/{case_id}/decision with reject."""
    # Create test case
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="ACC-REJ-001",
        source_email_id=f"rej-acc-{uuid.uuid4()}",
        source_address="rej@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Unclear",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    # Generate recommendation
    auth_client.post(f"/api/v1/classification/cases/{case_id}/recommendation")
    
    # Record reject decision
    response = auth_client.post(
        f"/api/v1/classification/cases/{case_id}/decision",
        json={
            "reviewer_decision": "reject",
            "reviewer_comment": "Not enough info",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["reviewer_decision"] == "reject"
    assert data["final_disruption_type"] is None


def test_post_decision_nonexistent_case_returns_400(auth_client):
    """Test POST decision for nonexistent case returns 400."""
    response = auth_client.post(
        "/api/v1/classification/cases/nonexistent/decision",
        json={
            "reviewer_decision": "confirm",
        },
    )
    
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_post_decision_without_pending_recommendation_returns_400(auth_client, db_session):
    """Test POST decision without pending recommendation returns 400."""
    # Create test case without recommendation
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="ACC-NO-REC-001",
        source_email_id=f"no-rec-{uuid.uuid4()}",
        source_address="test@test.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)
    db_session.commit()
    
    response = auth_client.post(
        f"/api/v1/classification/cases/{case_id}/decision",
        json={
            "reviewer_decision": "confirm",
        },
    )
    
    assert response.status_code == 400
    assert "No pending recommendation" in response.json()["detail"]
