"""Integration tests for VIN validation repository and service."""
from datetime import datetime, timezone
import json
import uuid

import pytest

from app.models.candidate_row import CandidateRow
from app.models.email_attachment import EmailAttachment
from app.models.intake_case import IntakeCase
from app.models.vin_record import VinRecord
from app.models.vin_validation_result import VinValidationResult
from app.repositories.vin_validation_result_repository import VinValidationResultRepository
from app.services.vin_processing_service import VinProcessingService


class TestVinValidationIntegration:
    """Integration tests for VIN validation with real database."""

    @pytest.fixture
    def test_case(self, db_session):
        """Create test intake case with VIN records."""
        # Create intake case
        case = IntakeCase(
            id=str(uuid.uuid4()),
            case_key="TEST-CASE-VAL",
            source_email_id=f"test-email-val-{uuid.uuid4()}",
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
        
        # Create candidate rows
        test_vins = [
            "1HGBH41J70N109186",  # Valid
            "1HGBH41JX",          # Wrong length
            "1HGBH41JXMN109I86",  # Invalid character
        ]
        
        vin_records = []
        for i, vin in enumerate(test_vins):
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
            vin_records.append(vin_record)
        
        db_session.commit()
        return case, vin_records

    def test_validation_result_repository_create(self, db_session, test_case):
        """Test creating validation results."""
        case, vin_records = test_case
        repo = VinValidationResultRepository(db_session)
        
        # Create validation result
        validation_result = VinValidationResult(
            id=str(uuid.uuid4()),
            vin_record_id=vin_records[0].id,
            validation_status="valid",
            failure_reason_code=None,
            failure_reason_detail=None,
            checksum_passed=True,
            validated_at_utc=datetime.now(timezone.utc),
        )
        
        result = repo.create(validation_result)
        db_session.commit()
        
        assert result.id == validation_result.id
        assert result.validation_status == "valid"
        assert result.checksum_passed is True

    def test_validation_result_repository_batch_create(self, db_session, test_case):
        """Test batch creating validation results."""
        case, vin_records = test_case
        repo = VinValidationResultRepository(db_session)
        
        # Create multiple validation results
        validation_results = []
        for vin_record in vin_records:
            validation_results.append(VinValidationResult(
                id=str(uuid.uuid4()),
                vin_record_id=vin_record.id,
                validation_status="valid",
                failure_reason_code=None,
                failure_reason_detail=None,
                checksum_passed=True,
                validated_at_utc=datetime.now(timezone.utc),
            ))
        
        results = repo.create_many(validation_results)
        db_session.commit()
        
        assert len(results) == 3
        
        # Verify all were created
        all_results = repo.get_by_case_id(case.id)
        assert len(all_results) == 3

    def test_validation_result_repository_get_by_vin_record(self, db_session, test_case):
        """Test getting validation result by VIN record ID."""
        case, vin_records = test_case
        repo = VinValidationResultRepository(db_session)
        
        # Create validation result
        validation_result = VinValidationResult(
            id=str(uuid.uuid4()),
            vin_record_id=vin_records[0].id,
            validation_status="valid",
            failure_reason_code=None,
            failure_reason_detail=None,
            checksum_passed=True,
            validated_at_utc=datetime.now(timezone.utc),
        )
        repo.create(validation_result)
        db_session.commit()
        
        # Get by VIN record ID
        result = repo.get_by_vin_record_id(vin_records[0].id)
        assert result is not None
        assert result.vin_record_id == vin_records[0].id

    def test_validation_result_repository_count_by_status(self, db_session, test_case):
        """Test counting validation results by status."""
        case, vin_records = test_case
        repo = VinValidationResultRepository(db_session)
        
        # Create validation results with different statuses
        repo.create(VinValidationResult(
            id=str(uuid.uuid4()),
            vin_record_id=vin_records[0].id,
            validation_status="valid",
            failure_reason_code=None,
            failure_reason_detail=None,
            checksum_passed=True,
            validated_at_utc=datetime.now(timezone.utc),
        ))
        
        repo.create(VinValidationResult(
            id=str(uuid.uuid4()),
            vin_record_id=vin_records[1].id,
            validation_status="invalid",
            failure_reason_code="wrong_length",
            failure_reason_detail="VIN too short",
            checksum_passed=False,
            validated_at_utc=datetime.now(timezone.utc),
        ))
        
        db_session.commit()
        
        # Count by status
        valid_count = repo.count_by_validation_status(case.id, "valid")
        invalid_count = repo.count_by_validation_status(case.id, "invalid")
        
        assert valid_count == 1
        assert invalid_count == 1

    def test_validation_result_repository_count_by_failure_reason(self, db_session, test_case):
        """Test counting validation results by failure reason."""
        case, vin_records = test_case
        repo = VinValidationResultRepository(db_session)
        
        # Create validation results with different failure reasons
        repo.create(VinValidationResult(
            id=str(uuid.uuid4()),
            vin_record_id=vin_records[1].id,
            validation_status="invalid",
            failure_reason_code="wrong_length",
            failure_reason_detail="VIN too short",
            checksum_passed=False,
            validated_at_utc=datetime.now(timezone.utc),
        ))
        
        repo.create(VinValidationResult(
            id=str(uuid.uuid4()),
            vin_record_id=vin_records[2].id,
            validation_status="invalid",
            failure_reason_code="invalid_character",
            failure_reason_detail="Forbidden character I",
            checksum_passed=False,
            validated_at_utc=datetime.now(timezone.utc),
        ))
        
        db_session.commit()
        
        # Count by failure reason
        wrong_length_count = repo.count_by_failure_reason(case.id, "wrong_length")
        invalid_char_count = repo.count_by_failure_reason(case.id, "invalid_character")
        checksum_count = repo.count_by_failure_reason(case.id, "checksum_failure")
        
        assert wrong_length_count == 1
        assert invalid_char_count == 1
        assert checksum_count == 0

    def test_validation_result_repository_delete_by_case(self, db_session, test_case):
        """Test deleting validation results for idempotent rerun."""
        case, vin_records = test_case
        repo = VinValidationResultRepository(db_session)
        
        # Create validation results
        for vin_record in vin_records:
            repo.create(VinValidationResult(
                id=str(uuid.uuid4()),
                vin_record_id=vin_record.id,
                validation_status="valid",
                failure_reason_code=None,
                failure_reason_detail=None,
                checksum_passed=True,
                validated_at_utc=datetime.now(timezone.utc),
            ))
        
        db_session.commit()
        
        # Verify created
        assert len(repo.get_by_case_id(case.id)) == 3
        
        # Delete all for case
        deleted_count = repo.delete_by_case_id(case.id)
        db_session.commit()
        
        assert deleted_count == 3
        assert len(repo.get_by_case_id(case.id)) == 0

    def test_vin_processing_service_validate_integration(self, db_session, test_case):
        """Test VIN processing service validation with real database."""
        case, vin_records = test_case
        service = VinProcessingService(db_session)
        
        # Run validation
        result = service.validate_vins(case.id)
        
        # Verify results
        assert result.case_id == case.id
        assert result.valid_count == 1
        assert result.invalid_count == 2
        assert result.failure_breakdown["wrong_length"] == 1
        assert result.failure_breakdown["invalid_character"] == 1
        
        # Verify validation results were persisted
        repo = VinValidationResultRepository(db_session)
        validation_results = repo.get_by_case_id(case.id)
        assert len(validation_results) == 3

    def test_vin_processing_service_idempotent_rerun(self, db_session, test_case):
        """Test validation can be rerun (idempotent)."""
        case, vin_records = test_case
        service = VinProcessingService(db_session)
        
        # Run validation first time
        result1 = service.validate_vins(case.id)
        
        # Verify results exist
        repo = VinValidationResultRepository(db_session)
        assert len(repo.get_by_case_id(case.id)) == 3
        
        # Run validation again
        result2 = service.validate_vins(case.id)
        
        # Verify results are consistent
        assert result1.valid_count == result2.valid_count
        assert result1.invalid_count == result2.invalid_count
        
        # Verify still only 3 results (old ones replaced)
        assert len(repo.get_by_case_id(case.id)) == 3

    def test_vin_processing_service_get_validation_summary(self, db_session, test_case):
        """Test getting full validation summary."""
        case, vin_records = test_case
        service = VinProcessingService(db_session)
        
        # Run validation
        service.validate_vins(case.id)
        
        # Get summary
        summary = service.get_validation_summary(case.id)
        
        # Verify summary
        assert summary.case_id == case.id
        assert summary.extracted == 3
        assert summary.valid == 1
        assert summary.invalid == 2
        assert summary.failure_reason_breakdown["wrong_length"] == 1
        assert summary.failure_reason_breakdown["invalid_character"] == 1
        assert summary.failure_reason_breakdown["checksum_failure"] == 0
        assert summary.failure_reason_breakdown["empty_value"] == 0
