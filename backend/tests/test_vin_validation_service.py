"""Unit tests for VIN validation service."""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import uuid

import pytest
from fastapi import HTTPException

from app.services.vin_processing_service import VinProcessingService


class TestVinValidationService:
    """Test VIN validation service methods."""

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create VinProcessingService with mocked session."""
        return VinProcessingService(mock_session)

    def test_validate_vins_case_not_found(self, service):
        """Test validation fails when case not found."""
        service.case_repo.get_by_id = MagicMock(return_value=None)
        
        with pytest.raises(HTTPException) as exc_info:
            service.validate_vins("nonexistent-case")
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_validate_vins_no_extracted_vins(self, service):
        """Test validation fails when no extracted VINs exist."""
        # Mock case exists
        mock_case = MagicMock()
        mock_case.id = "case-123"
        service.case_repo.get_by_id = MagicMock(return_value=mock_case)
        
        # Mock no extracted VINs
        service.vin_record_repo.get_by_case_id = MagicMock(return_value=[])
        
        with pytest.raises(HTTPException) as exc_info:
            service.validate_vins("case-123")
        
        assert exc_info.value.status_code == 400
        assert "no extracted vins" in exc_info.value.detail.lower()

    def test_validate_vins_success(self, service, mock_session):
        """Test successful VIN validation."""
        case_id = str(uuid.uuid4())
        
        # Mock case exists
        mock_case = MagicMock()
        mock_case.id = case_id
        service.case_repo.get_by_id = MagicMock(return_value=mock_case)
        
        # Mock extracted VIN records
        valid_vin_record = MagicMock()
        valid_vin_record.id = str(uuid.uuid4())
        valid_vin_record.normalized_vin = "1HGBH41J70N109186"
        valid_vin_record.extraction_status = "extracted"
        
        invalid_vin_record = MagicMock()
        invalid_vin_record.id = str(uuid.uuid4())
        invalid_vin_record.normalized_vin = "1HGBH41JX"
        invalid_vin_record.extraction_status = "extracted"
        
        service.vin_record_repo.get_by_case_id = MagicMock(
            return_value=[valid_vin_record, invalid_vin_record]
        )
        
        # Mock validation result repository
        service.validation_result_repo.delete_by_case_id = MagicMock(return_value=0)
        service.validation_result_repo.create_many = MagicMock(return_value=[])
        
        # Run validation
        result = service.validate_vins(case_id)
        
        # Verify results
        assert result.case_id == case_id
        assert result.valid_count == 1
        assert result.invalid_count == 1
        assert result.failure_breakdown["wrong_length"] == 1
        assert result.validated_at_utc is not None
        
        # Verify repositories were called
        service.validation_result_repo.delete_by_case_id.assert_called_once_with(case_id)
        service.validation_result_repo.create_many.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_validate_vins_idempotent_rerun(self, service, mock_session):
        """Test validation can be rerun (idempotent)."""
        case_id = str(uuid.uuid4())
        
        # Mock case exists
        mock_case = MagicMock()
        mock_case.id = case_id
        service.case_repo.get_by_id = MagicMock(return_value=mock_case)
        
        # Mock VIN records
        vin_record = MagicMock()
        vin_record.id = str(uuid.uuid4())
        vin_record.normalized_vin = "1HGBH41J70N109186"
        vin_record.extraction_status = "extracted"
        
        service.vin_record_repo.get_by_case_id = MagicMock(return_value=[vin_record])
        
        # Mock existing validation results are deleted
        service.validation_result_repo.delete_by_case_id = MagicMock(return_value=5)
        service.validation_result_repo.create_many = MagicMock(return_value=[])
        
        # Run validation
        result = service.validate_vins(case_id)
        
        # Verify old results were deleted
        service.validation_result_repo.delete_by_case_id.assert_called_once_with(case_id)
        mock_session.flush.assert_called_once()
        
        # Verify new results were created
        assert result.valid_count == 1
        assert result.invalid_count == 0

    def test_validate_vins_all_failure_reasons(self, service, mock_session):
        """Test validation captures all failure reason types."""
        case_id = str(uuid.uuid4())
        
        # Mock case exists
        mock_case = MagicMock()
        mock_case.id = case_id
        service.case_repo.get_by_id = MagicMock(return_value=mock_case)
        
        # Mock VIN records with different failure reasons
        vin_records = [
            # Valid
            MagicMock(id=str(uuid.uuid4()), normalized_vin="1HGBH41J70N109186", extraction_status="extracted"),
            # Wrong length
            MagicMock(id=str(uuid.uuid4()), normalized_vin="1HGBH41JX", extraction_status="extracted"),
            # Invalid character
            MagicMock(id=str(uuid.uuid4()), normalized_vin="1HGBH41JXMN109I86", extraction_status="extracted"),
            # Checksum failure
            MagicMock(id=str(uuid.uuid4()), normalized_vin="1HGBH41J00N109186", extraction_status="extracted"),
            # Empty (should not happen in extracted status, but test anyway)
            MagicMock(id=str(uuid.uuid4()), normalized_vin="", extraction_status="extracted"),
        ]
        
        service.vin_record_repo.get_by_case_id = MagicMock(return_value=vin_records)
        service.validation_result_repo.delete_by_case_id = MagicMock(return_value=0)
        service.validation_result_repo.create_many = MagicMock(return_value=[])
        
        # Run validation
        result = service.validate_vins(case_id)
        
        # Verify all failure reasons are captured
        assert result.valid_count == 1
        assert result.invalid_count == 4
        assert result.failure_breakdown["wrong_length"] == 1
        assert result.failure_breakdown["invalid_character"] == 1
        assert result.failure_breakdown["checksum_failure"] == 1
        assert result.failure_breakdown["empty_value"] == 1

    def test_get_validation_summary(self, service):
        """Test getting validation summary."""
        case_id = str(uuid.uuid4())
        
        # Mock case exists
        mock_case = MagicMock()
        mock_case.id = case_id
        service.case_repo.get_by_id = MagicMock(return_value=mock_case)
        
        # Mock extraction counts
        service.vin_record_repo.count_by_extraction_status = MagicMock(side_effect=[
            11,  # extracted
            1,   # rejected_empty
        ])
        service.vin_record_repo.count_duplicates = MagicMock(return_value=0)
        
        # Mock validation counts
        service.validation_result_repo.count_by_validation_status = MagicMock(side_effect=[
            8,  # valid
            3,  # invalid
        ])
        
        # Mock failure reason counts
        service.validation_result_repo.count_by_failure_reason = MagicMock(side_effect=[
            1,  # wrong_length
            1,  # invalid_character
            1,  # checksum_failure
            0,  # empty_value
        ])
        
        # Get summary
        summary = service.get_validation_summary(case_id)
        
        # Verify summary
        assert summary.case_id == case_id
        assert summary.extracted == 11
        assert summary.deduplicated == 0
        assert summary.rejected == 1
        assert summary.valid == 8
        assert summary.invalid == 3
        assert summary.failure_reason_breakdown["wrong_length"] == 1
        assert summary.failure_reason_breakdown["invalid_character"] == 1
        assert summary.failure_reason_breakdown["checksum_failure"] == 1
        assert summary.failure_reason_breakdown["empty_value"] == 0

    def test_get_validation_summary_case_not_found(self, service):
        """Test validation summary fails when case not found."""
        service.case_repo.get_by_id = MagicMock(return_value=None)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_validation_summary("nonexistent-case")
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_validate_vins_filters_non_extracted(self, service, mock_session):
        """Test validation only processes extracted VINs."""
        case_id = str(uuid.uuid4())
        
        # Mock case exists
        mock_case = MagicMock()
        mock_case.id = case_id
        service.case_repo.get_by_id = MagicMock(return_value=mock_case)
        
        # Mock VIN records with different statuses
        extracted_vin = MagicMock()
        extracted_vin.id = str(uuid.uuid4())
        extracted_vin.normalized_vin = "1HGBH41J70N109186"
        extracted_vin.extraction_status = "extracted"
        
        duplicate_vin = MagicMock()
        duplicate_vin.id = str(uuid.uuid4())
        duplicate_vin.normalized_vin = "1HGBH41J70N109186"
        duplicate_vin.extraction_status = "duplicate"
        
        rejected_vin = MagicMock()
        rejected_vin.id = str(uuid.uuid4())
        rejected_vin.normalized_vin = None
        rejected_vin.extraction_status = "rejected_empty"
        
        service.vin_record_repo.get_by_case_id = MagicMock(
            return_value=[extracted_vin, duplicate_vin, rejected_vin]
        )
        
        service.validation_result_repo.delete_by_case_id = MagicMock(return_value=0)
        service.validation_result_repo.create_many = MagicMock(return_value=[])
        
        # Run validation
        result = service.validate_vins(case_id)
        
        # Verify only extracted VIN was validated
        assert result.valid_count == 1
        assert result.invalid_count == 0
