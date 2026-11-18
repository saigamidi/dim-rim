/**
 * Type definitions for audit domain
 */

export interface AuditEventOut {
  id: string;
  intake_case_id: string;
  correlation_id: string;
  actor_type: string;
  actor_id: string;
  action_type: string;
  entity_type: string;
  entity_id: string;
  outcome: string;
  metadata_json: string;
  occurred_at_utc: string;
  created_at: string;
}
