export interface RiskLogEntry {
  log_entry_id: string;
  risk_id: string;

  // Entry metadata
  entry_date: string;
  entry_type: string;
  entry_summary: string;

  // Risk rating changes - Business Disruption model
  previous_net_exposure?: string;
  new_net_exposure?: string;
  previous_impact_rating?: string;
  new_impact_rating?: string;
  previous_likelihood_rating?: string;
  new_likelihood_rating?: string;

  // Actions and context
  mitigation_actions_taken?: string;
  risk_owner_at_time?: string;
  supporting_evidence?: string;

  // Workflow and approval
  entry_status: string;
  created_by: string;
  reviewed_by?: string;
  approved_date?: string;

  // Additional context
  business_justification?: string;
  next_review_required?: string;

  // Audit fields
  created_at: string;
  updated_at: string;
}

export interface RiskLogEntryCreate {
  risk_id: string;

  // Entry metadata
  entry_date: string;
  entry_type: string;
  entry_summary: string;

  // Risk rating changes - Business Disruption model
  previous_net_exposure?: string;
  new_net_exposure?: string;
  previous_impact_rating?: string;
  new_impact_rating?: string;
  previous_likelihood_rating?: string;
  new_likelihood_rating?: string;

  // Actions and context
  mitigation_actions_taken?: string;
  risk_owner_at_time?: string;
  supporting_evidence?: string;

  // Workflow and approval
  entry_status?: string;
  created_by: string;
  reviewed_by?: string;
  approved_date?: string;

  // Additional context
  business_justification?: string;
  next_review_required?: string;
}

export interface RiskLogEntryUpdate {
  // Entry metadata
  entry_date?: string;
  entry_type?: string;
  entry_summary?: string;

  // Risk rating changes - Business Disruption model
  previous_net_exposure?: string;
  new_net_exposure?: string;
  previous_impact_rating?: string;
  new_impact_rating?: string;
  previous_likelihood_rating?: string;
  new_likelihood_rating?: string;

  // Actions and context
  mitigation_actions_taken?: string;
  risk_owner_at_time?: string;
  supporting_evidence?: string;

  // Workflow and approval
  entry_status?: string;
  reviewed_by?: string;
  approved_date?: string;

  // Additional context
  business_justification?: string;
  next_review_required?: string;
}

export type RiskLogEntryStatus = 'Draft' | 'Submitted' | 'Approved' | 'Rejected';

export const RISK_LOG_ENTRY_TYPES = [
  'Risk Creation',
  'Risk Assessment Update',
  'Mitigation Completed',
  'Control Update',
  'Review Completed',
  'Status Change',
  'Owner Change',
  'General Update',
] as const;

export type RiskLogEntryType = typeof RISK_LOG_ENTRY_TYPES[number];
