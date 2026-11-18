"""Repository for audit event data access."""
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


class AuditEventRepository:
    """Repository for audit event CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, event: AuditEvent) -> AuditEvent:
        """Create a new audit event."""
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def get_by_case_id(self, case_id: str) -> list[AuditEvent]:
        """Get all audit events for a case, ordered by occurrence time."""
        return (
            self.session.query(AuditEvent)
            .filter(AuditEvent.intake_case_id == case_id)
            .order_by(AuditEvent.occurred_at_utc.asc())
            .all()
        )

    def get_by_correlation_id(self, correlation_id: str) -> list[AuditEvent]:
        """Get all audit events for a correlation ID."""
        return (
            self.session.query(AuditEvent)
            .filter(AuditEvent.correlation_id == correlation_id)
            .order_by(AuditEvent.occurred_at_utc.asc())
            .all()
        )
