"""Repository for intake case data access."""
from sqlalchemy.orm import Session, joinedload

from app.models.intake_case import IntakeCase


class IntakeCaseRepository:
    """Repository for intake case CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, intake_case: IntakeCase) -> IntakeCase:
        """Create a new intake case."""
        self.session.add(intake_case)
        self.session.commit()
        self.session.refresh(intake_case)
        return intake_case

    def get_by_id(self, case_id: str) -> IntakeCase | None:
        """Get intake case by ID or case_key with attachments."""
        # Try by ID first
        result = (
            self.session.query(IntakeCase)
            .options(joinedload(IntakeCase.attachments))
            .filter(IntakeCase.id == case_id)
            .first()
        )
        # If not found and looks like a case_key, try by case_key
        if not result and case_id.startswith("CASE-"):
            result = (
                self.session.query(IntakeCase)
                .options(joinedload(IntakeCase.attachments))
                .filter(IntakeCase.case_key == case_id)
                .first()
            )
        return result

    def get_by_source_email_id(self, source_email_id: str) -> IntakeCase | None:
        """Get intake case by source email ID."""
        return (
            self.session.query(IntakeCase)
            .filter(IntakeCase.source_email_id == source_email_id)
            .first()
        )

    def update_status(self, case_id: str, new_status: str) -> IntakeCase | None:
        """Update intake case status."""
        case = self.get_by_id(case_id)
        if case:
            case.intake_status = new_status
            self.session.commit()
            self.session.refresh(case)
        return case
