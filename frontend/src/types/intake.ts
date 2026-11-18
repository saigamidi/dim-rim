/**
 * Type definitions for intake domain
 */

export interface AttachmentOut {
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

export interface IntakeCaseOut {
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
  attachments: AttachmentOut[];
}

// Re-export CandidateRowOut from parsing domain for backward compatibility
export type { CandidateRowOut } from './parsing';
