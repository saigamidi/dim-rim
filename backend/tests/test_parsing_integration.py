"""Integration tests for parsing repositories."""
import json
import uuid
from datetime import datetime, timezone

from app.models.candidate_row import CandidateRow
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.repositories.candidate_row_repository import CandidateRowRepository


def test_candidate_row_repository_create(db_session):
    """Test creating a candidate row."""
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

    # Create candidate row
    repo = CandidateRowRepository(db_session)
    row = CandidateRow(
        id=str(uuid.uuid4()),
        attachment_id=attachment_id,
        source_row_number=1,
        canonical_vin_candidate="1HGBH41JXMN109186",
        raw_row_json=json.dumps({"vin": "1HGBH41JXMN109186"}),
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r1",
    )

    created_row = repo.create(row)
    db_session.commit()

    assert created_row.id is not None
    assert created_row.attachment_id == attachment_id
    assert created_row.canonical_vin_candidate == "1HGBH41JXMN109186"


def test_candidate_row_repository_create_many(db_session):
    """Test batch creating candidate rows."""
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

    # Create multiple candidate rows
    repo = CandidateRowRepository(db_session)
    rows = [
        CandidateRow(
            id=str(uuid.uuid4()),
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i}",
            raw_row_json=json.dumps({"vin": f"VIN{i}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        for i in range(1, 6)
    ]

    created_rows = repo.create_many(rows)
    db_session.commit()

    assert len(created_rows) == 5
    assert all(row.id is not None for row in created_rows)


def test_candidate_row_repository_get_by_attachment(db_session):
    """Test getting candidate rows by attachment ID."""
    # Create test data
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

    rows = [
        CandidateRow(
            id=str(uuid.uuid4()),
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i}",
            raw_row_json=json.dumps({"vin": f"VIN{i}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        for i in range(1, 4)
    ]
    for row in rows:
        db_session.add(row)
    db_session.commit()

    # Get rows by attachment
    repo = CandidateRowRepository(db_session)
    result = repo.get_by_attachment_id(attachment_id)

    assert len(result) == 3
    assert result[0].source_row_number == 1
    assert result[2].source_row_number == 3


def test_candidate_row_repository_delete_by_attachment(db_session):
    """Test deleting candidate rows by attachment ID."""
    # Create test data
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

    rows = [
        CandidateRow(
            id=str(uuid.uuid4()),
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i}",
            raw_row_json=json.dumps({"vin": f"VIN{i}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        for i in range(1, 4)
    ]
    for row in rows:
        db_session.add(row)
    db_session.commit()

    # Delete rows
    repo = CandidateRowRepository(db_session)
    deleted_count = repo.delete_by_attachment_id(attachment_id)
    db_session.commit()

    assert deleted_count == 3

    # Verify rows were deleted
    remaining = repo.get_by_attachment_id(attachment_id)
    assert len(remaining) == 0
