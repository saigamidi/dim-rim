"""Audit service for recording events."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.adapters.audit_writer_adapter import AuditWriterAdapter
from app.models.audit_event import AuditEvent
from app.repositories.audit_event_repository import AuditEventRepository
from app.schemas.audit_schemas import AuditEventOut


class AuditService:
    """Service for audit event recording and retrieval."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = AuditEventRepository(session)
        self.adapter = AuditWriterAdapter()

    def record_event(
        self,
        intake_case_id: str,
        correlation_id: str,
        actor_type: str,
        actor_id: str,
        action_type: str,
        entity_type: str,
        entity_id: str,
        outcome: str,
        metadata: dict[str, Any],
    ) -> AuditEventOut:
        """Record an audit event."""
        event = AuditEvent(
            id=str(uuid.uuid4()),
            intake_case_id=intake_case_id,
            correlation_id=correlation_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome=outcome,
            metadata_json=json.dumps(metadata),
            occurred_at_utc=datetime.now(timezone.utc),
        )
        
        created = self.repository.create(event)
        
        # Write to external audit system via TOL7
        self.adapter.write_audit_marker(
            case_id=intake_case_id,
            correlation_id=correlation_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome=outcome,
            metadata=metadata,
        )
        
        return AuditEventOut.model_validate(created)

    def get_case_events(self, case_id: str) -> list[AuditEventOut]:
        """Get all audit events for a case."""
        events = self.repository.get_by_case_id(case_id)
        return [AuditEventOut.model_validate(event) for event in events]

    def get_correlation_events(self, correlation_id: str) -> list[AuditEventOut]:
        """Get all audit events for a correlation ID."""
        events = self.repository.get_by_correlation_id(correlation_id)
        return [AuditEventOut.model_validate(event) for event in events]
