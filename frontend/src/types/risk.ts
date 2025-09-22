export interface Risk {
  // Core Risk Identification Fields
  risk_id: string;
  risk_title: string;
  risk_description: string;
  risk_category: string;

  // Risk Management Fields
  risk_status: string;
  risk_response_strategy: string;
  planned_mitigations?: string;

  // Control Management Fields - Updated naming
  preventative_controls_coverage: string;
  preventative_controls_effectiveness: string;
  preventative_controls_description?: string;
  detective_controls_coverage: string;
  detective_controls_effectiveness: string;
  detective_controls_description?: string;
  corrective_controls_coverage: string;
  corrective_controls_effectiveness: string;
  corrective_controls_description?: string;

  // Ownership & Systems Fields
  risk_owner: string;
  risk_owner_department: string;
  systems_affected?: string;
  technology_domain: string;

  // Business Disruption Assessment Fields - New model
  ibs_affected?: string;
  business_disruption_impact_rating: string; // Low/Moderate/Major/Catastrophic
  business_disruption_impact_description: string;
  business_disruption_likelihood_rating: string; // Remote/Unlikely/Possible/Probable
  business_disruption_likelihood_description: string;
  business_disruption_net_exposure: string; // Auto-calculated e.g. "Critical (15)"

  // Financial Impact Fields
  financial_impact_low?: number;
  financial_impact_high?: number;
  financial_impact_notes?: string;

  // Review & Timeline Fields
  date_identified: string;
  last_reviewed: string;
  next_review_date: string;
  created_at: string;
  updated_at: string;
}

export interface RiskUpdate {
  id: number;
  risk_id: number;
  field_name: string;
  old_value: string | null;
  new_value: string;
  change_reason: string;
  changed_by: string;
  change_date: string;
}

export interface DashboardData {
  total_active_risks: number;
  critical_high_risk_count: number;
  risk_trend_change: number;

  // Risk distribution
  risk_severity_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };

  technology_domain_risks: Array<{
    domain: string;
    risk_count: number;
    average_risk_rating: number;
  }>;

  // Control posture
  control_posture: {
    preventative_adequate_percentage: number;
    detective_adequate_percentage: number;
    corrective_adequate_percentage: number;
    risks_with_control_gaps: number;
  };

  top_priority_risks: Array<{
    risk_id: string;
    risk_title: string;
    business_disruption_net_exposure: string;
    financial_impact_high: number | null;
    ibs_affected: string | null;
    risk_owner: string;
  }>;

  risk_response_breakdown: {
    mitigate: number;
    accept: number;
    transfer: number;
    avoid: number;
  };

  total_financial_exposure: number;
  average_financial_impact: number;
  high_financial_impact_risks: number;

  risk_management_activity: {
    risks_reviewed_this_month: number;
    overdue_reviews: number;
    recent_risk_rating_changes: number;
  };

  business_service_exposure: {
    risks_affecting_ibs: number;
    total_ibs_affected: number;
    percentage_risks_with_ibs_impact: number;
    critical_risks_affecting_ibs: number;
  };
}

export interface DropdownValues {
  categories: string[];
  risk_response_strategies: string[];
  departments: string[];
  statuses: string[];
  technology_domains: string[];

  // New Business Disruption dropdowns
  business_disruption_impact_ratings: string[]; // Low, Moderate, Major, Catastrophic
  business_disruption_likelihood_ratings: string[]; // Remote, Unlikely, Possible, Probable

  // Updated control dropdowns
  controls_coverage: string[]; // Not Applicable, No Controls, Incomplete Coverage, Complete Coverage
  controls_effectiveness: string[]; // Not Applicable, Not Possible to Assess, Partially Effective, Fully Effective
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    pages: number;
    has_prev: boolean;
    has_next: boolean;
  };
}
