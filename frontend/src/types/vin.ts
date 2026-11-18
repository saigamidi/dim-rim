/**
 * Type definitions for VIN domain
 */

export interface VinExtractionRunOut {
  case_id: string;
  extracted_count: number;
  deduplicated_count: number;
  rejected_empty_count: number;
  run_status: string;
}

export interface VinRecordOut {
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

export interface VinExtractionSummaryOut {
  case_id: string;
  extracted: number;
  deduplicated: number;
  rejected: number;
}

export interface VinValidationResultOut {
  id: string;
  vin_record_id: string;
  validation_status: string;
  failure_reason_code: string | null;
  failure_reason_detail: string | null;
  checksum_passed: boolean;
  validated_at_utc: string;
  created_at: string;
}

export interface VinValidationRunOut {
  case_id: string;
  valid_count: number;
  invalid_count: number;
  failure_breakdown: Record<string, number>;
  validated_at_utc: string;
}

export interface VinValidationSummaryOut {
  case_id: string;
  extracted: number;
  deduplicated: number;
  rejected: number;
  valid: number;
  invalid: number;
  failure_reason_breakdown: Record<string, number>;
}
