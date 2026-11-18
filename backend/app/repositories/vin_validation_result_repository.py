"""Repository for VIN validation result operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vin_validation_result import VinValidationResult


class VinValidationResultRepository:
    """Repository for VIN validation result CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, validation_result: VinValidationResult) -> VinValidationResult:
        """Create a new VIN validation result."""
        self.session.add(validation_result)
        self.session.flush()
        return validation_result

    def create_many(self, validation_results: list[VinValidationResult]) -> list[VinValidationResult]:
        """Batch create VIN validation results."""
        self.session.add_all(validation_results)
        self.session.flush()
        return validation_results

    def get_by_id(self, validation_result_id: str) -> VinValidationResult | None:
        """Get validation result by ID."""
        return self.session.get(VinValidationResult, validation_result_id)

    def get_by_vin_record_id(self, vin_record_id: str) -> VinValidationResult | None:
        """Get validation result by VIN record ID."""
        stmt = select(VinValidationResult).where(
            VinValidationResult.vin_record_id == vin_record_id
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_case_id(self, case_id: str) -> list[VinValidationResult]:
        """Get all validation results for a case by joining through vin_record."""
        stmt = (
            select(VinValidationResult)
            .join(VinValidationResult.vin_record)
            .where(VinValidationResult.vin_record.has(intake_case_id=case_id))
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def count_by_validation_status(self, case_id: str, status: str) -> int:
        """Count validation results by status for a case."""
        from app.models.vin_record import VinRecord

        stmt = (
            select(VinValidationResult)
            .join(VinRecord, VinValidationResult.vin_record_id == VinRecord.id)
            .where(VinRecord.intake_case_id == case_id)
            .where(VinValidationResult.validation_status == status)
        )
        result = self.session.execute(stmt)
        return len(list(result.scalars().all()))

    def count_by_failure_reason(self, case_id: str, reason_code: str) -> int:
        """Count validation results by failure reason for a case."""
        from app.models.vin_record import VinRecord

        stmt = (
            select(VinValidationResult)
            .join(VinRecord, VinValidationResult.vin_record_id == VinRecord.id)
            .where(VinRecord.intake_case_id == case_id)
            .where(VinValidationResult.failure_reason_code == reason_code)
        )
        result = self.session.execute(stmt)
        return len(list(result.scalars().all()))

    def delete_by_case_id(self, case_id: str) -> int:
        """Delete all validation results for a case (for idempotent rerun)."""
        from app.models.vin_record import VinRecord

        stmt = select(VinValidationResult.id).join(
            VinRecord, VinValidationResult.vin_record_id == VinRecord.id
        ).where(VinRecord.intake_case_id == case_id)
        
        result = self.session.execute(stmt)
        validation_ids = [row[0] for row in result.all()]
        
        if validation_ids:
            for validation_id in validation_ids:
                validation_result = self.session.get(VinValidationResult, validation_id)
                if validation_result:
                    self.session.delete(validation_result)
        
        return len(validation_ids)
