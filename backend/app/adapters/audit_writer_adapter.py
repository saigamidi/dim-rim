"""TOL7 Audit Writer Adapter - Active implementation for MVP."""
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class AuditWriterAdapter:
    """Active audit writer adapter for recording events to external audit system.
    
    MVP: Writes structured log entries for audit trail.
    Future: May integrate with centralized audit/SIEM system.
    """

    def write_audit_marker(
        self,
        case_id: str,
        correlation_id: str,
        actor_type: str,
        actor_id: str,
        action_type: str,
        entity_type: str,
        entity_id: str,
        outcome: str,
        metadata: dict[str, Any],
    ) -> None:
        """Write audit marker to external audit system.
        
        MVP: Writes structured log entry.
        Future: May emit to centralized audit trail, SIEM, or compliance system.
        """
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "case_id": case_id,
            "correlation_id": correlation_id,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "action_type": action_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "outcome": outcome,
            "metadata": metadata,
        }
        
        logger.info(
            "AUDIT_MARKER",
            extra={
                "audit_entry": audit_entry,
                "structured": True,
            },
        )
        
    def write_external_marker(
        self, correlation_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        """Write external event marker for downstream systems.
        
        MVP: Structured log only.
        Future: Will emit to AGN5 downstream propagation seam for ETA, Dealer Daily, NSO.
        """
        external_marker = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "event_type": event_type,
            "payload": payload,
        }
        
        logger.info(
            "EXTERNAL_MARKER",
            extra={
                "external_marker": external_marker,
                "structured": True,
            },
        )
