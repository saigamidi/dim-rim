/**
 * Type definitions for classification domain
 */

export interface ClassificationRecommendationOut {
  id: string;
  intake_case_id: string;
  suggested_disruption_type: string;
  suggested_disruption_subtype: string | null;
  suggested_event_ref: string | null;
  confidence_score: number;
  created_at: string;
}

export interface ClassificationDecisionIn {
  reviewer_decision: 'confirm' | 'revise' | 'reject';
  final_disruption_type?: string | null;
  final_disruption_subtype?: string | null;
  final_event_ref?: string | null;
  reviewer_comment?: string | null;
}

export interface ClassificationDecisionOut {
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
