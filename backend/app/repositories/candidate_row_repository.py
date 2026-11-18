"""Candidate row repository for parsed row persistence."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_row import CandidateRow


class CandidateRowRepository:
    """Repository for candidate row operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, candidate_row: CandidateRow) -> CandidateRow:
        """Create a new candidate row."""
        self.session.add(candidate_row)
        self.session.flush()
        self.session.refresh(candidate_row)
        return candidate_row

    def create_many(self, candidate_rows: list[CandidateRow]) -> list[CandidateRow]:
        """Create multiple candidate rows in a batch."""
        self.session.add_all(candidate_rows)
        self.session.flush()
        for row in candidate_rows:
            self.session.refresh(row)
        return candidate_rows

    def get_by_id(self, row_id: str) -> CandidateRow | None:
        """Get candidate row by ID."""
        return self.session.get(CandidateRow, row_id)

    def get_by_attachment_id(self, attachment_id: str) -> list[CandidateRow]:
        """Get all candidate rows for an attachment."""
        stmt = select(CandidateRow).where(CandidateRow.attachment_id == attachment_id).order_by(CandidateRow.source_row_number)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_case_id(self, case_id: str) -> list[CandidateRow]:
        """Get all candidate rows for a case through attachment relationship."""
        stmt = (
            select(CandidateRow)
            .join(CandidateRow.attachment)
            .where(CandidateRow.attachment.has(intake_case_id=case_id))
            .order_by(CandidateRow.source_row_number)
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def count_by_attachment_id(self, attachment_id: str) -> int:
        """Count candidate rows for an attachment."""
        stmt = select(CandidateRow).where(CandidateRow.attachment_id == attachment_id)
        result = self.session.execute(stmt)
        return len(list(result.scalars().all()))

    def delete_by_attachment_id(self, attachment_id: str) -> int:
        """Delete all candidate rows for an attachment (for reparse)."""
        rows = self.get_by_attachment_id(attachment_id)
        count = len(rows)
        for row in rows:
            self.session.delete(row)
        self.session.flush()
        return count
