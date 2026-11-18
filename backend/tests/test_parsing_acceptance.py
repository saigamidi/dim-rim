"""Acceptance tests for parsing endpoints."""
import json
import uuid
from datetime import datetime, timezone

import pytest

from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase


def test_parse_attachment_endpoint_success(auth_client, db_session):
    """Test POST /api/v1/parsing/attachments/{attachment_id}/parse endpoint."""
    # Create test case and attachment
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="TEST-001",
        source_email_id="test@example.com",
        source_address="sender@example.com",
        received_at_utc=datetime.now(timezone.utc),
subject="Test Subject",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)

    attachment_id = str(uuid.uuid4())
    attachment = EmailAttachment(
        id=attachment_id,
        intake_case_id=case_id,
        filename="test.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        byte_size=1000,
        storage_ref="test/path",
        parse_status="pending",
    )
    db_session.add(attachment)
    db_session.commit()

    # Parse attachment
    response = auth_client.post(
        f"/api/v1/parsing/attachments/{attachment_id}/parse",
        json={"force_reparse": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["attachment_id"] == attachment_id
    assert data["parse_status"] == "parsed"
    assert data["row_count"] == 8  # Mocked adapter returns 8 rows
    assert data["failure_count"] == 0
    assert "lineage_base_ref" in data


def test_parse_attachment_force_reparse(auth_client, db_session):
    """Test force reparse of already parsed attachment."""
    # Create test case and attachment
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="TEST-001",
        source_email_id="test@example.com",
        source_address="sender@example.com",
        received_at_utc=datetime.now(timezone.utc),
subject="Test Subject",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)

    attachment_id = str(uuid.uuid4())
    attachment = EmailAttachment(
        id=attachment_id,
        intake_case_id=case_id,
        filename="test.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        byte_size=1000,
        storage_ref="test/path",
        parse_status="parsed",
    )
    db_session.add(attachment)
    db_session.commit()

    # Force reparse
    response = auth_client.post(
        f"/api/v1/parsing/attachments/{attachment_id}/parse",
        json={"force_reparse": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["parse_status"] == "parsed"


def test_parse_attachment_not_found(auth_client, db_session):
    """Test parsing non-existent attachment returns 404."""
    response = auth_client.post(
        "/api/v1/parsing/attachments/nonexistent-id/parse",
        json={"force_reparse": False},
    )

    assert response.status_code == 404


def test_parse_attachment_unauthorized(client, db_session):
    """Test parsing without authentication returns 401."""
    attachment_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/parsing/attachments/{attachment_id}/parse",
        json={"force_reparse": False},
    )

    assert response.status_code == 401


def test_get_candidate_rows_endpoint(auth_client, db_session):
    """Test GET /api/v1/parsing/cases/{case_id}/rows endpoint."""
    from app.models.candidate_row import CandidateRow
    
    # Create test case with attachment and rows
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="TEST-001",
        source_email_id="test@example.com",
        source_address="sender@example.com",
        received_at_utc=datetime.now(timezone.utc),
subject="Test Subject",
        intake_status="parsed",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)

    attachment_id = str(uuid.uuid4())
    attachment = EmailAttachment(
        id=attachment_id,
        intake_case_id=case_id,
        filename="test.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        byte_size=1000,
        storage_ref="test/path",
        parse_status="parsed",
    )
    db_session.add(attachment)
    
    # Create candidate rows directly
    for i in range(1, 9):
        row = CandidateRow(
            id=str(uuid.uuid4()),
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i:03d}",
            raw_row_json=json.dumps({"vin": f"VIN{i:03d}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        db_session.add(row)
    db_session.commit()

    # Get candidate rows
    response = auth_client.get(f"/api/v1/parsing/cases/{case_id}/rows")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 8  # Mocked adapter returns 8 rows
    
    # Verify row structure
    row = data[0]
    assert "id" in row
    assert "attachment_id" in row
    assert "source_row_number" in row
    assert "canonical_vin_candidate" in row
    assert "row_status" in row
    assert "lineage_ref" in row


def test_get_candidate_rows_unauthorized(client, db_session):
    """Test getting candidate rows without authentication returns 401."""
    case_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/parsing/cases/{case_id}/rows")

    assert response.status_code == 401


def test_parsing_preserves_lineage(auth_client, db_session):
    """Test that parsing preserves row-level lineage."""
    # Create test case and attachment
    case_id = str(uuid.uuid4())
    case = IntakeCase(
        id=case_id,
        case_key="TEST-001",
        source_email_id="test@example.com",
        source_address="sender@example.com",
        received_at_utc=datetime.now(timezone.utc),
subject="Test Subject",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(case)

    attachment_id = str(uuid.uuid4())
    attachment = EmailAttachment(
        id=attachment_id,
        intake_case_id=case_id,
        filename="test.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        byte_size=1000,
        storage_ref="test/path",
        parse_status="pending",
    )
    db_session.add(attachment)
    db_session.commit()

    # Parse attachment
    auth_client.post(
        f"/api/v1/parsing/attachments/{attachment_id}/parse",
        json={"force_reparse": False},
    )

    # Get candidate rows
    response = auth_client.get(f"/api/v1/parsing/cases/{case_id}/rows")
    rows = response.json()

    # Verify lineage format: lin-{case_id}/att-{attachment_id}/r{row_num}
    for i, row in enumerate(rows, start=1):
        expected_lineage = f"lin-{case_id}/att-{attachment_id}/r{i}"
        assert row["lineage_ref"] == expected_lineage
        assert row["source_row_number"] == i
