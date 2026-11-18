"""Repository for classification decision data access."""
from sqlalchemy.orm import Session

from app.models.classification_decision import ClassificationDecision


class ClassificationDecisionRepository:
    """Repository for classification decision CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, decision: ClassificationDecision) -> ClassificationDecision:
        """Create a new classification decision."""
        self.session.add(decision)
        self.session.commit()
        self.session.refresh(decision)
        return decision

    def get_by_id(self, decision_id: str) -> ClassificationDecision | None:
        """Get classification decision by ID."""
        return (
            self.session.query(ClassificationDecision)
            .filter(ClassificationDecision.id == decision_id)
            .first()
        )

    def get_by_case_id(self, case_id: str) -> ClassificationDecision | None:
        """Get latest classification decision for a case."""
        return (
            self.session.query(ClassificationDecision)
            .filter(ClassificationDecision.intake_case_id == case_id)
            .order_by(ClassificationDecision.created_at.desc())
            .first()
        )
