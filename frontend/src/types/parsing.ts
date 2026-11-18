/**
 * Type definitions for parsing domain
 */

export interface AttachmentParseRequest {
  force_reparse?: boolean;
}

export interface AttachmentParseResultOut {
  attachment_id: string;
  parse_status: string;
  row_count: number;
  failure_count: number;
  lineage_base_ref: string;
}

export interface CandidateRowOut {
  id: string;
  attachment_id: string;
  source_row_number: number;
  canonical_vin_candidate: string | null;
  raw_row_json: string;
  row_status: string;
  lineage_ref: string;
  created_at: string;
}
