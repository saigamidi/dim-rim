/**
 * TypeScript interfaces mirroring backend SQLAlchemy models.
 * All fields use snake_case to match API responses.
 */

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface IntakeCase {
  id: string;
  case_key: string;
  source_email_id: string;
  source_address: string;
  received_at_utc: string;
  subject: string;
  intake_status: string;
  correlation_id: string;
  created_at: string;
  updated_at: string;
}

export interface EmailAttachment {
  id: string;
  intake_case_id: string;
  filename: string;
  media_type: string;
  byte_size: number;
  storage_ref: string;
  parse_status: string;
  created_at: string;
  updated_at: string;
}

export interface CandidateRow {
  id: string;
  attachment_id: string;
  source_row_number: number;
  canonical_vin_candidate: string | null;
  raw_row_json: string;
  row_status: string;
  lineage_ref: string;
  created_at: string;
}

export interface ClassificationDecision {
  id: string;
  intake_case_id: string;
  suggested_disruption_type: string;
  suggested_disruption_subtype: string | null;
  suggested_event_ref: string | null;
  confidence_score: number;
  reviewer_decision: string;
  final_disruption_type: string | null;
  final_disruption_subtype: string | null;
  final_event_ref: string | null;
  reviewer_comment: string | null;
  decided_by_user_id: string;
  decided_at_utc: string;
  created_at: string;
}

export interface VinRecord {
  id: string;
  intake_case_id: string;
  candidate_row_id: string;
  raw_vin: string | null;
  normalized_vin: string | null;
  extraction_status: string;
  is_duplicate_within_case: boolean;
  created_at: string;
  updated_at: string;
}

export interface VinValidationResult {
  id: string;
  vin_record_id: string;
  validation_status: string;
  failure_reason_code: string | null;
  failure_reason_detail: string | null;
  checksum_passed: boolean;
  validated_at_utc: string;
  created_at: string;
}

export interface AuditEvent {
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

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthUser {
  token: string;
  user: User;
}
