"""Acceptance tests for VIN validation endpoints."""
from datetime import datetime, timezone
import json
import uuid

import pytest

from app.models.audit_event import AuditEvent
from app.models.candidate_row import CandidateRow
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.models.vin_record import VinRecord


class TestVinValidationAcceptance:
    """
    Acceptance tests for FR-005: VIN Validation.
    
    FR-005 acceptance criteria:
    - Every candidate VIN is checked for length, character validity, and checksum rules
    - Invalid VINs are routed into exception buckets with explicit failure reasons
    - No invalid VIN proceeds to the confirmation or load-preparation path
    - Validation outcomes are persisted in an auditable form per VIN
    """

    @pytest.fixture
    def test_case_with_vins(self, db_session):
        """Create test case with extracted VINs."""
        # Create intake case
        case = IntakeCase(
            id=str(uuid.uuid4()),
            case_key=f"TEST-VAL-{uuid.uuid4().hex[:8]}",
            source_email_id=f"test-email-{uuid.uuid4()}",
            source_address="test@example.com",
            received_at_utc=datetime.now(timezone.utc),
            subject="Test VIN Validation",
            intake_status="parsed",
            correlation_id=str(uuid.uuid4()),
        )
        db_session.add(case)
        
        # Create attachment
        attachment = EmailAttachment(
            id=str(uuid.uuid4()),
            intake_case_id=case.id,
            filename="test_vins.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            byte_size=1000,
            storage_ref=f"test/{uuid.uuid4()}",
            parse_status="parsed",
        )
        db_session.add(attachment)
        
        # Create candidate rows and VIN records with diverse validation outcomes
        test_vins = [
            ("1HGBH41J70N109186", "valid"),           # Valid
            ("2HGBH41J60N109187", "valid"),           # Valid
            ("1HGBH41JX", "wrong_length"),            # Too short
            ("1HGBH41JXMN109I86", "invalid_character"),  # Has 'I'
            ("1HGBH41J00N109186", "checksum_failure"),   # Wrong check digit
        ]
        
        for i, (vin, expected_outcome) in enumerate(test_vins):
            row = CandidateRow(
                id=str(uuid.uuid4()),
                attachment_id=attachment.id,
                source_row_number=i + 1,
                canonical_vin_candidate=vin,
                raw_row_json=json.dumps({"vin": vin}),
                row_status="extracted",
                lineage_ref=f"test-{i+1}",
            )
            db_session.add(row)
            
            # Create extracted VIN record
            vin_record = VinRecord(
                id=str(uuid.uuid4()),
                intake_case_id=case.id,
                candidate_row_id=row.id,
                raw_vin=vin,
                normalized_vin=vin.upper().strip(),
                extraction_status="extracted",
                is_duplicate_within_case=False,
            )
            db_session.add(vin_record)
        
        db_session.commit()
        return case

    def test_validate_vins_success(self, auth_client, test_case_with_vins):
        """Test successful VIN validation."""
        case = test_case_with_vins
        
        # Validate VINs
        response = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["case_id"] == case.id
        assert "valid_count" in data
        assert "invalid_count" in data
        assert "failure_breakdown" in data
        assert "validated_at_utc" in data
        
        # Verify counts
        assert data["valid_count"] == 2
        assert data["invalid_count"] == 3
        
        # Verify failure breakdown
        assert data["failure_breakdown"]["wrong_length"] == 1
        assert data["failure_breakdown"]["invalid_character"] == 1
        assert data["failure_breakdown"]["checksum_failure"] == 1
        assert data["failure_breakdown"]["empty_value"] == 0

    def test_validate_vins_case_not_found(self, auth_client):
        """Test validation with nonexistent case."""
        response = auth_client.post(f"/api/v1/vins/cases/{uuid.uuid4()}/validate")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_validate_vins_no_extracted_vins(self, auth_client, db_session):
        """Test validation with no extracted VINs."""
        # Create case without VIN records
        case = IntakeCase(
            id=str(uuid.uuid4()),
            case_key=f"TEST-EMPTY-{uuid.uuid4().hex[:8]}",
            source_email_id=f"test-email-{uuid.uuid4()}",
            source_address="test@example.com",
            received_at_utc=datetime.now(timezone.utc),
            subject="Test Empty Case",
            intake_status="parsed",
            correlation_id=str(uuid.uuid4()),
        )
        db_session.add(case)
        db_session.commit()
        
        # Try to validate
        response = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        
        assert response.status_code == 400
        assert "no extracted vins" in response.json()["detail"].lower()

    def test_validate_vins_requires_auth(self, client, test_case_with_vins):
        """Test validation requires authentication."""
        case = test_case_with_vins
        
        response = client.post(f"/api/v1/vins/cases/{case.id}/validate")
        
        assert response.status_code == 401

    def test_validate_vins_creates_audit_event(self, auth_client, db_session, test_case_with_vins):
        """Test validation creates audit event."""
        case = test_case_with_vins
        
        # Count audit events before
        before_count = db_session.query(AuditEvent).filter(
            AuditEvent.intake_case_id == case.id,
            AuditEvent.action_type == "vins_validated"
        ).count()
        
        # Validate VINs
        response = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        assert response.status_code == 200
        
        # Verify audit event created
        after_count = db_session.query(AuditEvent).filter(
            AuditEvent.intake_case_id == case.id,
            AuditEvent.action_type == "vins_validated"
        ).count()
        
        assert after_count == before_count + 1
        
        # Verify audit event details
        audit_event = db_session.query(AuditEvent).filter(
            AuditEvent.intake_case_id == case.id,
            AuditEvent.action_type == "vins_validated"
        ).order_by(AuditEvent.created_at.desc()).first()
        
        assert audit_event is not None
        assert audit_event.actor_type == "user"
        assert audit_event.outcome == "success"
        
        metadata = json.loads(audit_event.metadata_json)
        assert "valid_count" in metadata
        assert "invalid_count" in metadata
        assert "failure_breakdown" in metadata

    def test_validate_vins_idempotent(self, auth_client, test_case_with_vins):
        """Test validation is idempotent (can be rerun)."""
        case = test_case_with_vins
        
        # Run validation first time
        response1 = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Run validation second time
        response2 = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Verify results are consistent
        assert data1["valid_count"] == data2["valid_count"]
        assert data1["invalid_count"] == data2["invalid_count"]
        assert data1["failure_breakdown"] == data2["failure_breakdown"]

    def test_get_validation_summary(self, auth_client, test_case_with_vins):
        """Test getting full validation summary."""
        case = test_case_with_vins
        
        # Run validation
        validate_response = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        assert validate_response.status_code == 200
        
        # Get summary
        response = auth_client.get(f"/api/v1/vins/cases/{case.id}/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify summary structure
        assert data["case_id"] == case.id
        assert "extracted" in data
        assert "deduplicated" in data
        assert "rejected" in data
        assert "valid" in data
        assert "invalid" in data
        assert "failure_reason_breakdown" in data
        
        # Verify extraction counts
        assert data["extracted"] == 5
        assert data["deduplicated"] == 0
        assert data["rejected"] == 0
        
        # Verify validation counts
        assert data["valid"] == 2
        assert data["invalid"] == 3
        
        # Verify failure breakdown
        assert data["failure_reason_breakdown"]["wrong_length"] == 1
        assert data["failure_reason_breakdown"]["invalid_character"] == 1
        assert data["failure_reason_breakdown"]["checksum_failure"] == 1
        assert data["failure_reason_breakdown"]["empty_value"] == 0

    def test_validation_outcomes_persisted(self, auth_client, db_session, test_case_with_vins):
        """
        FR-005: Validation outcomes are persisted in an auditable form per VIN.
        """
        case = test_case_with_vins
        
        # Run validation
        response = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        assert response.status_code == 200
        
        # Verify validation results are persisted
        from app.models.vin_validation_result import VinValidationResult
        from app.repositories.vin_validation_result_repository import VinValidationResultRepository
        
        repo = VinValidationResultRepository(db_session)
        validation_results = repo.get_by_case_id(case.id)
        
        # Verify one result per extracted VIN
        assert len(validation_results) == 5
        
        # Verify each result has required fields
        for result in validation_results:
            assert result.vin_record_id is not None
            assert result.validation_status in ["valid", "invalid"]
            assert result.checksum_passed in [True, False]
            assert result.validated_at_utc is not None

    def test_invalid_vins_have_explicit_failure_reasons(self, auth_client, db_session, test_case_with_vins):
        """
        FR-005: Invalid VINs are routed into exception buckets with explicit failure reasons.
        """
        case = test_case_with_vins
        
        # Run validation
        response = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        assert response.status_code == 200
        
        # Get validation results
        from app.repositories.vin_validation_result_repository import VinValidationResultRepository
        
        repo = VinValidationResultRepository(db_session)
        validation_results = repo.get_by_case_id(case.id)
        
        # Find invalid results
        invalid_results = [r for r in validation_results if r.validation_status == "invalid"]
        
        # Verify all invalid VINs have explicit failure reasons
        assert len(invalid_results) == 3
        
        for result in invalid_results:
            assert result.failure_reason_code is not None
            assert result.failure_reason_code in [
                "wrong_length",
                "invalid_character",
                "checksum_failure",
                "empty_value"
            ]
            assert result.failure_reason_detail is not None
            assert len(result.failure_reason_detail) > 0

    def test_validation_checks_length_characters_checksum(self, auth_client, test_case_with_vins):
        """
        FR-005: Every candidate VIN is checked for length, character validity, and checksum rules.
        """
        case = test_case_with_vins
        
        # Run validation
        response = auth_client.post(f"/api/v1/vins/cases/{case.id}/validate")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all three failure types are captured
        breakdown = data["failure_breakdown"]
        
        # Length check
        assert breakdown["wrong_length"] >= 1
        
        # Character validity check
        assert breakdown["invalid_character"] >= 1
        
        # Checksum check
        assert breakdown["checksum_failure"] >= 1

    def test_get_summary_before_validation(self, auth_client, test_case_with_vins):
        """Test getting summary before validation shows zero validation counts."""
        case = test_case_with_vins
        
        # Get summary before validation
        response = auth_client.get(f"/api/v1/vins/cases/{case.id}/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Extraction counts should exist
        assert data["extracted"] == 5
        
        # Validation counts should be zero
        assert data["valid"] == 0
        assert data["invalid"] == 0
        assert all(count == 0 for count in data["failure_reason_breakdown"].values())
