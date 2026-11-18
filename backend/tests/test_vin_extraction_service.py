"""Unit tests for VIN extraction service."""
import json
import uuid
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.models.candidate_row import CandidateRow
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.models.vin_record import VinRecord
from app.services.vin_processing_service import VinProcessingService


def test_extract_vins_success(db_session):
    """Test successful VIN extraction with normalization and deduplication."""
    # Create test case
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

    # Create attachment
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

    # Create candidate rows with some duplicates and empty values
    rows = [
        ("1HGBH41JXMN109186", 1),
        ("  1hgbh41jxmn109186  ", 2),  # Duplicate (different case/whitespace)
        ("2HGFA16588H123456", 3),
        ("", 4),  # Empty
        (None, 5),  # Null
        ("3FTFW1ET5BKE12345", 6),
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
    service = VinProcessingService(db_session)
    result = service.extract_vins(case_id)

    assert result.case_id == case_id
    assert result.extracted_count == 3  # Unique VINs (first occurrence of duplicate kept)
    assert result.deduplicated_count == 1  # One duplicate
    assert result.rejected_empty_count == 2  # Empty and null
    assert result.run_status == "completed"

    # Verify VIN records were created
    vin_records = db_session.query(VinRecord).filter_by(intake_case_id=case_id).all()
    assert len(vin_records) == 6  # All rows processed

    # Check extracted (unique) VINs
    extracted = [r for r in vin_records if r.extraction_status == "extracted"]
    assert len(extracted) == 3
    assert all(r.normalized_vin is not None for r in extracted)
    assert all(not r.is_duplicate_within_case for r in extracted)

    # Check duplicate VINs
    duplicates = [r for r in vin_records if r.extraction_status == "duplicate"]
    assert len(duplicates) == 1
    assert duplicates[0].is_duplicate_within_case
    assert duplicates[0].normalized_vin == "1HGBH41JXMN109186"

    # Check rejected (empty) VINs
    rejected = [r for r in vin_records if r.extraction_status == "rejected_empty"]
    assert len(rejected) == 2


def test_extract_vins_case_not_found(db_session):
    """Test extraction for non-existent case raises 404."""
    service = VinProcessingService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        service.extract_vins("nonexistent-case-id")
    
    assert exc_info.value.status_code == 404


def test_extract_vins_no_candidate_rows(db_session):
    """Test extraction with no candidate rows raises 400."""
    # Create test case without candidate rows
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
    db_session.commit()

    service = VinProcessingService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        service.extract_vins(case_id)
    
    assert exc_info.value.status_code == 400
    assert "No candidate rows found" in str(exc_info.value.detail)


def test_extract_vins_normalization(db_session):
    """Test VIN normalization (uppercase, trim whitespace)."""
    # Create test case
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

    # Create attachment
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

    # Create candidate row with lowercase and whitespace
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
    service = VinProcessingService(db_session)
    result = service.extract_vins(case_id)

    # Verify normalization
    vin_records = db_session.query(VinRecord).filter_by(intake_case_id=case_id).all()
    assert len(vin_records) == 1
    assert vin_records[0].raw_vin == "  1hgbh41jxmn109186  "
    assert vin_records[0].normalized_vin == "1HGBH41JXMN109186"


def test_get_extraction_summary(db_session):
    """Test getting VIN extraction summary."""
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
        
        vin = VinRecord(
            id=str(uuid.uuid4()),
            intake_case_id=case_id,
            candidate_row_id=row_id,
            raw_vin=f"VIN{i}",
            normalized_vin=f"VIN{i}",
            extraction_status="extracted",
            is_duplicate_within_case=False,
        )
        db_session.add(vin)

    # Add duplicate
    row_id = str(uuid.uuid4())
    row = CandidateRow(
        id=row_id,
        attachment_id=attachment_id,
        source_row_number=10,
        canonical_vin_candidate="VIN0",
        raw_row_json=json.dumps({"vin": "VIN0"}),
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r10",
    )
    db_session.add(row)
    
    vin = VinRecord(
        id=str(uuid.uuid4()),
        intake_case_id=case_id,
        candidate_row_id=row_id,
        raw_vin="VIN0",
        normalized_vin="VIN0",
        extraction_status="duplicate",
        is_duplicate_within_case=True,
    )
    db_session.add(vin)

    # Add rejected
    row_id = str(uuid.uuid4())
    row = CandidateRow(
        id=row_id,
        attachment_id=attachment_id,
        source_row_number=11,
        canonical_vin_candidate="",
        raw_row_json=json.dumps({"vin": ""}),
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r11",
    )
    db_session.add(row)
    
    vin = VinRecord(
        id=str(uuid.uuid4()),
        intake_case_id=case_id,
        candidate_row_id=row_id,
        raw_vin="",
        normalized_vin=None,
        extraction_status="rejected_empty",
        is_duplicate_within_case=False,
    )
    db_session.add(vin)

    db_session.commit()

    # Get summary
    service = VinProcessingService(db_session)
    summary = service.get_extraction_summary(case_id)

    assert summary.case_id == case_id
    assert summary.extracted == 3
    assert summary.deduplicated == 1
    assert summary.rejected == 1
