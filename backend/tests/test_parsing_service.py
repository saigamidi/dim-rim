"""Unit tests for attachment parsing service."""
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.candidate_row import CandidateRow
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.services.attachment_parsing_service import AttachmentParsingService


def test_parse_attachment_success(db_session):
    """Test successful attachment parsing."""
    # Create parent intake case
    attachment_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    intake_case = IntakeCase(
        id=case_id,
        case_key=f"CASE-TEST-{case_id[:8]}",
        source_email_id="test@example.com",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(intake_case)
    # Create test attachment
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

    # Mock parser adapter
    with patch("app.services.attachment_parsing_service.AttachmentParserAdapter") as MockAdapter:
        mock_adapter_instance = MockAdapter.return_value
        mock_adapter_instance.validate_attachment_format.return_value = (True, None)
        
        # Mock parsed rows
        from app.adapters.attachment_parser_adapter import ParsedRow
        mock_parsed_rows = [
            ParsedRow(1, "1HGBH41JXMN109186", {"vin": "1HGBH41JXMN109186"}),
            ParsedRow(2, "2HGFA16588H123456", {"vin": "2HGFA16588H123456"}),
        ]
        mock_adapter_instance.parse_attachment.return_value = (mock_parsed_rows, 0)

        service = AttachmentParsingService(db_session)
        result = service.parse_attachment(attachment_id)

        assert result.attachment_id == attachment_id
        assert result.parse_status == "parsed"
        assert result.row_count == 2
        assert result.failure_count == 0
        assert f"lin-{case_id}" in result.lineage_base_ref

        # Verify candidate rows were created
        rows = db_session.query(CandidateRow).filter_by(attachment_id=attachment_id).all()
        assert len(rows) == 2
        assert rows[0].canonical_vin_candidate == "1HGBH41JXMN109186"
        assert rows[1].canonical_vin_candidate == "2HGFA16588H123456"


def test_parse_attachment_already_parsed(db_session):
    """Test parsing already parsed attachment returns existing results."""
    # Create parent intake case
    attachment_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    intake_case = IntakeCase(
        id=case_id,
        case_key=f"CASE-TEST-{case_id[:8]}",
        source_email_id="test@example.com",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(intake_case)
    # Create test attachment with parsed status
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

    # Add existing candidate rows
    row1 = CandidateRow(
        id=str(uuid.uuid4()),
        attachment_id=attachment_id,
        source_row_number=1,
        canonical_vin_candidate="1HGBH41JXMN109186",
        raw_row_json=json.dumps({"vin": "1HGBH41JXMN109186"}),
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r1",
    )
    db_session.add(row1)
    db_session.commit()

    service = AttachmentParsingService(db_session)
    result = service.parse_attachment(attachment_id, force_reparse=False)

    assert result.parse_status == "parsed"
    assert result.row_count == 1


def test_parse_attachment_force_reparse(db_session):
    """Test force reparse deletes existing rows and reparses."""
    # Create parent intake case
    attachment_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    intake_case = IntakeCase(
        id=case_id,
        case_key=f"CASE-TEST-{case_id[:8]}",
        source_email_id="test@example.com",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(intake_case)
    # Create test attachment with parsed status
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

    # Add existing candidate row
    row1 = CandidateRow(
        id=str(uuid.uuid4()),
        attachment_id=attachment_id,
        source_row_number=1,
        canonical_vin_candidate="OLD_VIN",
        raw_row_json=json.dumps({"vin": "OLD_VIN"}),
        row_status="parsed",
        lineage_ref=f"lin-{case_id}/att-{attachment_id}/r1",
    )
    db_session.add(row1)
    db_session.commit()

    # Mock parser adapter
    with patch("app.services.attachment_parsing_service.AttachmentParserAdapter") as MockAdapter:
        mock_adapter_instance = MockAdapter.return_value
        mock_adapter_instance.validate_attachment_format.return_value = (True, None)
        
        from app.adapters.attachment_parser_adapter import ParsedRow
        mock_parsed_rows = [
            ParsedRow(1, "NEW_VIN", {"vin": "NEW_VIN"}),
        ]
        mock_adapter_instance.parse_attachment.return_value = (mock_parsed_rows, 0)

        service = AttachmentParsingService(db_session)
        result = service.parse_attachment(attachment_id, force_reparse=True)

        assert result.parse_status == "parsed"
        assert result.row_count == 1

        # Verify old row was deleted and new one created
        rows = db_session.query(CandidateRow).filter_by(attachment_id=attachment_id).all()
        assert len(rows) == 1
        assert rows[0].canonical_vin_candidate == "NEW_VIN"


def test_parse_attachment_not_found(db_session):
    """Test parsing non-existent attachment raises 404."""
    service = AttachmentParsingService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        service.parse_attachment("nonexistent-id")
    
    assert exc_info.value.status_code == 404


def test_parse_attachment_unsupported_format(db_session):
    """Test parsing unsupported format raises 400."""
    # Create parent intake case
    attachment_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    intake_case = IntakeCase(
        id=case_id,
        case_key=f"CASE-TEST-{case_id[:8]}",
        source_email_id="test@example.com",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(intake_case)
    # Create test attachment with unsupported media type
    attachment = EmailAttachment(
        id=attachment_id,
        intake_case_id=case_id,
        filename="test.pdf",
        media_type="application/pdf",
        byte_size=1000,
        storage_ref="test/path",
        parse_status="pending",
    )
    db_session.add(attachment)
    db_session.commit()

    with patch("app.services.attachment_parsing_service.AttachmentParserAdapter") as MockAdapter:
        mock_adapter_instance = MockAdapter.return_value
        mock_adapter_instance.validate_attachment_format.return_value = (False, "Unsupported media type")

        service = AttachmentParsingService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.parse_attachment(attachment_id)
        
        assert exc_info.value.status_code == 400
        
        # Verify parse status was updated to failed
        db_session.refresh(attachment)
        assert attachment.parse_status == "parse_failed"


def test_get_candidate_rows_by_case(db_session):
    """Test retrieving candidate rows by case ID."""
    # Create parent intake case
    case_id = str(uuid.uuid4())
    intake_case = IntakeCase(
        id=case_id,
        case_key=f"CASE-TEST-{case_id[:8]}",
        source_email_id="test@example.com",
        source_address="test@example.com",
        received_at_utc=datetime.now(timezone.utc),
        subject="Test",
        intake_status="received",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(intake_case)
    # Create test data
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

    service = AttachmentParsingService(db_session)
    result = service.get_candidate_rows_by_case(case_id)

    assert len(result) == 3
    assert result[0].canonical_vin_candidate == "VIN1"
    assert result[2].canonical_vin_candidate == "VIN3"
