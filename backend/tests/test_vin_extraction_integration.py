"""Integration tests for VIN extraction repositories."""
import json
import uuid
from datetime import datetime, timezone

from app.models.candidate_row import CandidateRow
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.models.vin_record import VinRecord
from app.repositories.vin_record_repository import VinRecordRepository


def test_vin_record_repository_create(db_session):
    """Test creating a VIN record."""
    # Create test case, attachment, and candidate row
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

    row_id = str(uuid.uuid4())
    row = CandidateRow(
        id=row_id,
        attachment_id=attachment_id,
        source_row_number=1,
        canonical_vin_candidate="1HGBH41JXMN109186",
        raw_row_json='{"vin": "1HGBH41JXMN109186"}',
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r1",
    )
    db_session.add(row)
    db_session.commit()

    # Create VIN record
    repo = VinRecordRepository(db_session)
    vin_record = VinRecord(
        id=str(uuid.uuid4()),
        intake_case_id=case_id,
        candidate_row_id=row_id,
        raw_vin="1HGBH41JXMN109186",
        normalized_vin="1HGBH41JXMN109186",
        extraction_status="extracted",
        is_duplicate_within_case=False,
    )

    created_record = repo.create(vin_record)
    db_session.commit()

    assert created_record.id is not None
    assert created_record.intake_case_id == case_id
    assert created_record.normalized_vin == "1HGBH41JXMN109186"


def test_vin_record_repository_create_many(db_session):
    """Test batch creating VIN records."""
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
    
    # Create candidate rows
    row_ids = []
    for i in range(1, 6):
        row_id = str(uuid.uuid4())
        row = CandidateRow(
            id=row_id,
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i}",
            raw_row_json=json.dumps({"vin": f"VIN{i}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        db_session.add(row)
        row_ids.append(row_id)
    db_session.commit()

    # Create multiple VIN records
    repo = VinRecordRepository(db_session)
    records = [
        VinRecord(
            id=str(uuid.uuid4()),
            intake_case_id=case_id,
            candidate_row_id=row_ids[i-1],
            raw_vin=f"VIN{i}",
            normalized_vin=f"VIN{i}",
            extraction_status="extracted",
            is_duplicate_within_case=False,
        )
        for i in range(1, 6)
    ]

    created_records = repo.create_many(records)
    db_session.commit()

    assert len(created_records) == 5
    assert all(record.id is not None for record in created_records)


def test_vin_record_repository_get_by_case(db_session):
    """Test getting VIN records by case ID."""
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
    
    # Create candidate rows and VIN records
    for i in range(1, 4):
        row_id = str(uuid.uuid4())
        row = CandidateRow(
            id=row_id,
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i}",
            raw_row_json=json.dumps({"vin": f"VIN{i}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        db_session.add(row)
        
        record = VinRecord(
            id=str(uuid.uuid4()),
            intake_case_id=case_id,
            candidate_row_id=row_id,
            raw_vin=f"VIN{i}",
            normalized_vin=f"VIN{i}",
            extraction_status="extracted",
            is_duplicate_within_case=False,
        )
        db_session.add(record)
    db_session.commit()

    # Get records by case
    repo = VinRecordRepository(db_session)
    result = repo.get_by_case_id(case_id)

    assert len(result) == 3


def test_vin_record_repository_count_by_extraction_status(db_session):
    """Test counting VIN records by extraction status."""
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

    # Create candidate rows and VIN records with different statuses
    for i in range(3):
        row_id = str(uuid.uuid4())
        row = CandidateRow(
            id=row_id,
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i}",
            raw_row_json=json.dumps({"vin": f"VIN{i}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        db_session.add(row)
        
        record = VinRecord(
            id=str(uuid.uuid4()),
            intake_case_id=case_id,
            candidate_row_id=row_id,
            raw_vin=f"VIN{i}",
            normalized_vin=f"VIN{i}",
            extraction_status="extracted",
            is_duplicate_within_case=False,
        )
        db_session.add(record)

    for i in range(2):
        row_id = str(uuid.uuid4())
        row = CandidateRow(
            id=row_id,
            attachment_id=attachment_id,
            source_row_number=i+10,
            canonical_vin_candidate="",
            raw_row_json=json.dumps({"vin": ""}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i+10}",
        )
        db_session.add(row)
        
        record = VinRecord(
            id=str(uuid.uuid4()),
            intake_case_id=case_id,
            candidate_row_id=row_id,
            raw_vin="",
            normalized_vin=None,
            extraction_status="rejected_empty",
            is_duplicate_within_case=False,
        )
        db_session.add(record)

    db_session.commit()

    # Count by status
    repo = VinRecordRepository(db_session)
    extracted_count = repo.count_by_extraction_status(case_id, "extracted")
    rejected_count = repo.count_by_extraction_status(case_id, "rejected_empty")

    assert extracted_count == 3
    assert rejected_count == 2


def test_vin_record_repository_count_duplicates(db_session):
    """Test counting duplicate VIN records."""
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

    # Create unique VIN records
    for i in range(3):
        row_id = str(uuid.uuid4())
        row = CandidateRow(
            id=row_id,
            attachment_id=attachment_id,
            source_row_number=i,
            canonical_vin_candidate=f"VIN{i}",
            raw_row_json=json.dumps({"vin": f"VIN{i}"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i}",
        )
        db_session.add(row)
        
        record = VinRecord(
            id=str(uuid.uuid4()),
            intake_case_id=case_id,
            candidate_row_id=row_id,
            raw_vin=f"VIN{i}",
            normalized_vin=f"VIN{i}",
            extraction_status="extracted",
            is_duplicate_within_case=False,
        )
        db_session.add(record)

    # Create duplicate VIN records
    for i in range(2):
        row_id = str(uuid.uuid4())
        row = CandidateRow(
            id=row_id,
            attachment_id=attachment_id,
            source_row_number=i+10,
            canonical_vin_candidate="DUPLICATE",
            raw_row_json=json.dumps({"vin": "DUPLICATE"}),
            row_status="parsed",
            lineage_ref=f"lin-{case_id}/att-{attachment_id}/r{i+10}",
        )
        db_session.add(row)
        
        record = VinRecord(
            id=str(uuid.uuid4()),
            intake_case_id=case_id,
            candidate_row_id=row_id,
            raw_vin="VIN0",
            normalized_vin="VIN0",
            extraction_status="duplicate",
            is_duplicate_within_case=True,
        )
        db_session.add(record)

    db_session.commit()

    # Count duplicates
    repo = VinRecordRepository(db_session)
    duplicate_count = repo.count_duplicates(case_id)

    assert duplicate_count == 2
