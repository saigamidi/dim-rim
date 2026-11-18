"""Acceptance tests for VIN extraction endpoints."""
import json
import uuid
from datetime import datetime, timezone

import pytest

from app.models.candidate_row import CandidateRow
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase


def test_extract_vins_endpoint_success(auth_client, db_session):
    """Test POST /api/v1/vins/cases/{case_id}/extract endpoint."""
    # Create test case with candidate rows
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

    # Create candidate rows with some duplicates and empties
    rows = [
        ("1HGBH41JXMN109186", 1),
        ("  1hgbh41jxmn109186  ", 2),  # Duplicate
        ("2HGFA16588H123456", 3),
        ("", 4),  # Empty
    ]

    for vin, row_num in rows:
        row = CandidateRow(
            id=str(uuid.uuid4()),
            attachment_id=attachment_id,
            source_row_number=row_num,
            canonical_vin_candidate=vin,
            raw_row_json=json.dumps({"vin": vin}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{row_num}",
        )
        db_session.add(row)
    
    db_session.commit()

    # Extract VINs
    response = auth_client.post(f"/api/v1/vins/cases/{case_id}/extract")

    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == case_id
    assert data["extracted_count"] == 2  # Unique VINs
    assert data["deduplicated_count"] == 1  # Duplicate
    assert data["rejected_empty_count"] == 1  # Empty
    assert data["run_status"] == "completed"


def test_extract_vins_normalization(auth_client, db_session):
    """Test VIN normalization during extraction."""
    # Create test case with lowercase and whitespace VINs
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

    row = CandidateRow(
        id=str(uuid.uuid4()),
        attachment_id=attachment_id,
        source_row_number=1,
        canonical_vin_candidate="  1hgbh41jxmn109186  ",
        raw_row_json=json.dumps({"vin": "  1hgbh41jxmn109186  "}),
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r1",
    )
    db_session.add(row)
    db_session.commit()

    # Extract VINs
    response = auth_client.post(f"/api/v1/vins/cases/{case_id}/extract")

    assert response.status_code == 200
    data = response.json()
    assert data["extracted_count"] == 1


def test_extract_vins_case_not_found(auth_client, db_session):
    """Test extraction for non-existent case returns 404."""
    response = auth_client.post("/api/v1/vins/cases/nonexistent-id/extract")

    assert response.status_code == 404


def test_extract_vins_no_candidate_rows(auth_client, db_session):
    """Test extraction with no candidate rows returns 400."""
    # Create case without candidate rows
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
    db_session.commit()

    response = auth_client.post(f"/api/v1/vins/cases/{case_id}/extract")

    assert response.status_code == 400
    assert "No candidate rows found" in response.json()["detail"]


def test_extract_vins_unauthorized(client, db_session):
    """Test extraction without authentication returns 401."""
    case_id = str(uuid.uuid4())
    response = client.post(f"/api/v1/vins/cases/{case_id}/extract")

    assert response.status_code == 401


def test_get_vin_summary_endpoint(auth_client, db_session):
    """Test GET /api/v1/vins/cases/{case_id}/summary endpoint."""
    # Create test case with VIN records
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

    # Create candidate rows
    rows = [
        ("1HGBH41JXMN109186", 1),
        ("  1hgbh41jxmn109186  ", 2),  # Duplicate
        ("2HGFA16588H123456", 3),
        ("", 4),  # Empty
    ]

    for vin, row_num in rows:
        row = CandidateRow(
            id=str(uuid.uuid4()),
            attachment_id=attachment_id,
            source_row_number=row_num,
            canonical_vin_candidate=vin,
            raw_row_json=json.dumps({"vin": vin}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{row_num}",
        )
        db_session.add(row)
    
    db_session.commit()

    # Extract VINs first
    auth_client.post(f"/api/v1/vins/cases/{case_id}/extract")

    # Get summary
    response = auth_client.get(f"/api/v1/vins/cases/{case_id}/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == case_id
    assert data["extracted"] == 2  # Unique VINs
    assert data["deduplicated"] == 1  # Duplicates
    assert data["rejected"] == 1  # Empty


def test_get_vin_summary_case_not_found(auth_client, db_session):
    """Test getting summary for non-existent case returns 404."""
    response = auth_client.get("/api/v1/vins/cases/nonexistent-id/summary")

    assert response.status_code == 404


def test_get_vin_summary_unauthorized(client, db_session):
    """Test getting summary without authentication returns 401."""
    case_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/vins/cases/{case_id}/summary")

    assert response.status_code == 401


def test_extraction_idempotent(auth_client, db_session):
    """Test VIN extraction is idempotent (can be rerun)."""
    # Create test case with candidate rows
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

    row = CandidateRow(
        id=str(uuid.uuid4()),
        attachment_id=attachment_id,
        source_row_number=1,
        canonical_vin_candidate="1HGBH41JXMN109186",
        raw_row_json=json.dumps({"vin": "1HGBH41JXMN109186"}),
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r1",
    )
    db_session.add(row)
    db_session.commit()

    # Run extraction twice
    response1 = auth_client.post(f"/api/v1/vins/cases/{case_id}/extract")
    response2 = auth_client.post(f"/api/v1/vins/cases/{case_id}/extract")

    # Both should succeed (idempotent)
    assert response1.status_code == 200
    assert response2.status_code == 200
