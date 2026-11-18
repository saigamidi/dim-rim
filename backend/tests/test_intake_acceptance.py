"""Acceptance tests for intake endpoints (full HTTP flow)."""
import uuid
from datetime import datetime, timezone


def test_post_intake_submission_creates_case(auth_client, db_session):
    """Test POST /api/v1/intake/submissions creates intake case."""
    response = auth_client.post(
        "/api/v1/intake/submissions",
        json={
            "source_email_id": f"acc-test-{uuid.uuid4()}",
            "source_address": "acceptance@test.com",
            "received_at_utc": datetime.now(timezone.utc).isoformat(),
            "subject": "Acceptance Test Disruption",
            "has_attachments": True,
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["case_key"].startswith("CASE-")
    assert data["source_address"] == "acceptance@test.com"
    assert data["intake_status"] == "received"
    assert len(data["attachments"]) == 1


def test_post_intake_submission_non_candidate_returns_400(auth_client):
    """Test POST /api/v1/intake/submissions with non-candidate returns 400."""
    response = auth_client.post(
        "/api/v1/intake/submissions",
        json={
            "source_email_id": f"non-candidate-{uuid.uuid4()}",
            "source_address": "test@example.com",
            "received_at_utc": datetime.now(timezone.utc).isoformat(),
            "subject": "Regular email",
            "has_attachments": False,
        },
    )
    
    assert response.status_code == 400
    assert "not a disruption candidate" in response.json()["detail"]


def test_get_intake_case_returns_case(auth_client, db_session):
    """Test GET /api/v1/intake/cases/{case_id} returns case."""
    # First create a case
    create_response = auth_client.post(
        "/api/v1/intake/submissions",
        json={
            "source_email_id": f"get-test-{uuid.uuid4()}",
            "source_address": "get@test.com",
            "received_at_utc": datetime.now(timezone.utc).isoformat(),
            "subject": "Get Test Disruption",
            "has_attachments": False,
        },
    )
    assert create_response.status_code == 201
    case_id = create_response.json()["id"]
    
    # Get the case
    response = auth_client.get(f"/api/v1/intake/cases/{case_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == case_id
    assert data["source_address"] == "get@test.com"


def test_get_intake_case_nonexistent_returns_404(auth_client):
    """Test GET /api/v1/intake/cases/{case_id} for nonexistent returns 404."""
    response = auth_client.get("/api/v1/intake/cases/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_post_intake_submission_requires_auth(client):
    """Test POST /api/v1/intake/submissions requires authentication."""
    response = client.post(
        "/api/v1/intake/submissions",
        json={
            "source_email_id": f"unauth-{uuid.uuid4()}",
            "source_address": "test@example.com",
            "received_at_utc": datetime.now(timezone.utc).isoformat(),
            "subject": "Test",
            "has_attachments": False,
        },
    )
    
    assert response.status_code == 401  # HTTPBearer returns 401 without credentials
