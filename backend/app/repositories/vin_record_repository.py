"""VIN record repository for VIN persistence."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vin_record import VinRecord


class VinRecordRepository:
    """Repository for VIN record operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, vin_record: VinRecord) -> VinRecord:
        """Create a new VIN record."""
        self.session.add(vin_record)
        self.session.flush()
        self.session.refresh(vin_record)
        return vin_record

    def create_many(self, vin_records: list[VinRecord]) -> list[VinRecord]:
        """Create multiple VIN records in a batch."""
        self.session.add_all(vin_records)
        self.session.flush()
        for record in vin_records:
            self.session.refresh(record)
        return vin_records

    def get_by_id(self, record_id: str) -> VinRecord | None:
        """Get VIN record by ID."""
        return self.session.get(VinRecord, record_id)

    def get_by_case_id(self, case_id: str) -> list[VinRecord]:
        """Get all VIN records for a case."""
        stmt = select(VinRecord).where(VinRecord.intake_case_id == case_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_normalized_vin_in_case(self, case_id: str, normalized_vin: str) -> VinRecord | None:
        """Get first VIN record with matching normalized VIN in a case."""
        stmt = (
            select(VinRecord)
            .where(VinRecord.intake_case_id == case_id)
            .where(VinRecord.normalized_vin == normalized_vin)
            .order_by(VinRecord.created_at)
        )
        result = self.session.execute(stmt)
        return result.scalars().first()

    def count_by_case_id(self, case_id: str) -> int:
        """Count VIN records for a case."""
        stmt = select(VinRecord).where(VinRecord.intake_case_id == case_id)
        result = self.session.execute(stmt)
        return len(list(result.scalars().all()))

    def count_by_extraction_status(self, case_id: str, status: str) -> int:
        """Count VIN records by extraction status for a case."""
        stmt = (
            select(VinRecord)
            .where(VinRecord.intake_case_id == case_id)
            .where(VinRecord.extraction_status == status)
        )
        result = self.session.execute(stmt)
        return len(list(result.scalars().all()))

    def count_duplicates(self, case_id: str) -> int:
        """Count duplicate VIN records for a case."""
        stmt = (
            select(VinRecord)
            .where(VinRecord.intake_case_id == case_id)
            .where(VinRecord.is_duplicate_within_case == True)  # noqa: E712
        )
        result = self.session.execute(stmt)
        return len(list(result.scalars().all()))

    def delete_by_case_id(self, case_id: str) -> int:
        """Delete all VIN records for a case (for re-extraction)."""
        records = self.get_by_case_id(case_id)
        count = len(records)
        for record in records:
            self.session.delete(record)
        self.session.flush()
        return count
