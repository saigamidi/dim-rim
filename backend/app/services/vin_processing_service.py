"""VIN processing service for extraction, normalization, and deduplication."""
import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.vin_record import VinRecord
from app.models.vin_validation_result import VinValidationResult
from app.repositories.candidate_row_repository import CandidateRowRepository
from app.repositories.intake_case_repository import IntakeCaseRepository
from app.repositories.vin_record_repository import VinRecordRepository
from app.repositories.vin_validation_result_repository import VinValidationResultRepository
from app.schemas.vin_schemas import (
    VinExtractionRunOut,
    VinExtractionSummaryOut,
    VinRecordOut,
    VinValidationRunOut,
    VinValidationSummaryOut,
)
from app.services.deterministic_rule_engine import DeterministicRuleEngine

logger = logging.getLogger(__name__)


class VinProcessingService:
    """Service for VIN extraction and processing operations."""

    def __init__(self, session: Session):
        self.session = session
        self.case_repo = IntakeCaseRepository(session)
        self.candidate_row_repo = CandidateRowRepository(session)
        self.vin_record_repo = VinRecordRepository(session)
        self.validation_result_repo = VinValidationResultRepository(session)
        self.rule_engine = DeterministicRuleEngine()

    def extract_vins(self, case_id: str) -> VinExtractionRunOut:
        """
        Extract VINs from candidate rows.
        
        Normalizes (uppercase, trim whitespace), deduplicates within case
        (first occurrence kept, lineage preserved), produces counts.
        Idempotent rerun allowed.
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        # Get candidate rows
        candidate_rows = self.candidate_row_repo.get_by_case_id(case_id)
        if not candidate_rows:
            raise HTTPException(
                status_code=400,
                detail=f"No candidate rows found for case {case_id}. Parse attachments first."
            )

        # Track seen normalized VINs for deduplication
        seen_vins: dict[str, str] = {}  # normalized_vin -> first_candidate_row_id
        
        extracted_count = 0
        deduplicated_count = 0
        rejected_count = 0
        
        vin_records = []

        for row in candidate_rows:
            # Skip empty/null VIN candidates
            if not row.canonical_vin_candidate or not row.canonical_vin_candidate.strip():
                rejected_count += 1
                # Create rejected record
                vin_record = VinRecord(
                    id=str(uuid.uuid4()),
                    intake_case_id=case_id,
                    candidate_row_id=row.id,
                    raw_vin=row.canonical_vin_candidate,
                    normalized_vin=None,
                    extraction_status="rejected_empty",
                    is_duplicate_within_case=False,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                vin_records.append(vin_record)
                continue

            # Normalize VIN: uppercase, trim whitespace
            raw_vin = row.canonical_vin_candidate
            normalized_vin = raw_vin.strip().upper()

            # Check for duplicate within case
            if normalized_vin in seen_vins:
                # Duplicate found
                deduplicated_count += 1
                vin_record = VinRecord(
                    id=str(uuid.uuid4()),
                    intake_case_id=case_id,
                    candidate_row_id=row.id,
                    raw_vin=raw_vin,
                    normalized_vin=normalized_vin,
                    extraction_status="duplicate",
                    is_duplicate_within_case=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                vin_records.append(vin_record)
            else:
                # First occurrence - keep it
                extracted_count += 1
                seen_vins[normalized_vin] = row.id
                vin_record = VinRecord(
                    id=str(uuid.uuid4()),
                    intake_case_id=case_id,
                    candidate_row_id=row.id,
                    raw_vin=raw_vin,
                    normalized_vin=normalized_vin,
                    extraction_status="extracted",
                    is_duplicate_within_case=False,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                vin_records.append(vin_record)

        # Batch insert VIN records
        if vin_records:
            self.vin_record_repo.create_many(vin_records)

        self.session.commit()

        logger.info(
            f"VIN extraction complete for case {case_id}: "
            f"{extracted_count} extracted, {deduplicated_count} deduplicated, {rejected_count} rejected"
        )

        return VinExtractionRunOut(
            case_id=case_id,
            extracted_count=extracted_count,
            deduplicated_count=deduplicated_count,
            rejected_empty_count=rejected_count,
            run_status="completed",
        )

    def get_extraction_summary(self, case_id: str) -> VinExtractionSummaryOut:
        """
        Get VIN extraction summary counts.
        
        Returns counts of extracted, deduplicated, and rejected VINs.
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        # Count by extraction status
        extracted_count = self.vin_record_repo.count_by_extraction_status(case_id, "extracted")
        deduplicated_count = self.vin_record_repo.count_duplicates(case_id)
        rejected_count = self.vin_record_repo.count_by_extraction_status(case_id, "rejected_empty")

        return VinExtractionSummaryOut(
            case_id=case_id,
            extracted=extracted_count,
            deduplicated=deduplicated_count,
            rejected=rejected_count,
        )

    def get_vin_records_by_case(self, case_id: str) -> list[VinRecordOut]:
        """Get all VIN records for a case."""
        records = self.vin_record_repo.get_by_case_id(case_id)
        return [VinRecordOut.model_validate(record) for record in records]

    def get_vin_records_with_validation(self, case_id: str) -> list[dict]:
        """
        Get all VIN records for a case with validation results.
        
        Returns list of VIN records including extraction status and validation results.
        """
        records = self.vin_record_repo.get_by_case_id(case_id)
        
        # Convert to response schema
        result = []
        for record in records:
            validation_result = None
            if record.validation_result:
                validation_result = {
                    "validation_status": record.validation_result.validation_status,
                    "failure_reason_code": record.validation_result.failure_reason_code,
                    "failure_reason_detail": record.validation_result.failure_reason_detail,
                    "checksum_passed": record.validation_result.checksum_passed,
                    "validated_at_utc": record.validation_result.validated_at_utc,
                }
            
            result.append({
                "id": record.id,
                "normalized_vin": record.normalized_vin,
                "raw_vin": record.raw_vin,
                "extraction_status": record.extraction_status,
                "is_duplicate_within_case": record.is_duplicate_within_case,
                "validation_result": validation_result,
            })
        
        return result

    def validate_vins(self, case_id: str) -> VinValidationRunOut:
        """
        Run BR-01 deterministic validation on extracted VINs.
        
        Validates length, character validity, and checksum rules.
        Persists explicit failure reason codes. Invalid VINs blocked
        from future lookup/load paths. Idempotent rerun allowed.
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        # Get extracted VIN records (status = "extracted")
        vin_records = self.vin_record_repo.get_by_case_id(case_id)
        
        # Filter to only extracted VINs (not duplicates or rejected)
        extracted_vins = [
            record for record in vin_records
            if record.extraction_status == "extracted"
        ]

        if not extracted_vins:
            raise HTTPException(
                status_code=400,
                detail=f"No extracted VINs found for case {case_id}. Run extraction first."
            )

        # Delete existing validation results for idempotent rerun
        deleted_count = self.validation_result_repo.delete_by_case_id(case_id)
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} existing validation results for case {case_id}")
            self.session.flush()

        # Validate each VIN
        valid_count = 0
        invalid_count = 0
        failure_breakdown: dict[str, int] = {
            "wrong_length": 0,
            "invalid_character": 0,
            "checksum_failure": 0,
            "empty_value": 0,
        }

        validation_results = []
        validated_at = datetime.now(timezone.utc)

        for vin_record in extracted_vins:
            # Normalize VIN (already normalized during extraction, but re-normalize for safety)
            normalized_vin = vin_record.normalized_vin or ""
            
            # Run BR-01 validation
            validation = self.rule_engine.validate_vin(normalized_vin)

            # Determine status
            if validation.is_valid:
                status = "valid"
                valid_count += 1
            else:
                status = "invalid"
                invalid_count += 1
                # Increment failure reason breakdown
                if validation.failure_reason_code:
                    failure_breakdown[validation.failure_reason_code] = (
                        failure_breakdown.get(validation.failure_reason_code, 0) + 1
                    )

            # Create validation result record
            validation_result = VinValidationResult(
                id=str(uuid.uuid4()),
                vin_record_id=vin_record.id,
                validation_status=status,
                failure_reason_code=validation.failure_reason_code,
                failure_reason_detail=validation.failure_reason_detail,
                checksum_passed=validation.checksum_passed,
                validated_at_utc=validated_at,
                created_at=datetime.now(timezone.utc),
            )
            validation_results.append(validation_result)

        # Batch insert validation results
        if validation_results:
            self.validation_result_repo.create_many(validation_results)

        self.session.commit()

        logger.info(
            f"VIN validation complete for case {case_id}: "
            f"{valid_count} valid, {invalid_count} invalid"
        )

        return VinValidationRunOut(
            case_id=case_id,
            valid_count=valid_count,
            invalid_count=invalid_count,
            failure_breakdown=failure_breakdown,
            validated_at_utc=validated_at,
        )

    def get_validation_summary(self, case_id: str) -> VinValidationSummaryOut:
        """
        Get full VIN summary including extraction and validation counts.
        
        Returns extraction counts (extracted, deduplicated, rejected) and
        validation counts (valid, invalid, failure_reason_breakdown).
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        # Get extraction counts
        extracted_count = self.vin_record_repo.count_by_extraction_status(case_id, "extracted")
        deduplicated_count = self.vin_record_repo.count_duplicates(case_id)
        rejected_count = self.vin_record_repo.count_by_extraction_status(case_id, "rejected_empty")

        # Get validation counts
        valid_count = self.validation_result_repo.count_by_validation_status(case_id, "valid")
        invalid_count = self.validation_result_repo.count_by_validation_status(case_id, "invalid")

        # Get failure reason breakdown
        failure_breakdown = {
            "wrong_length": self.validation_result_repo.count_by_failure_reason(
                case_id, "wrong_length"
            ),
            "invalid_character": self.validation_result_repo.count_by_failure_reason(
                case_id, "invalid_character"
            ),
            "checksum_failure": self.validation_result_repo.count_by_failure_reason(
                case_id, "checksum_failure"
            ),
            "empty_value": self.validation_result_repo.count_by_failure_reason(
                case_id, "empty_value"
            ),
        }

        return VinValidationSummaryOut(
            case_id=case_id,
            extracted=extracted_count,
            deduplicated=deduplicated_count,
            rejected=rejected_count,
            valid=valid_count,
            invalid=invalid_count,
            failure_reason_breakdown=failure_breakdown,
        )
