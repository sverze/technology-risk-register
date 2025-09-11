export interface Risk {
  risk_id: string;
  risk_title: string;
  risk_description: string;
  risk_category: string;
  inherent_probability: number;
  inherent_impact: number;
  current_probability: number;
  current_impact: number;
  inherent_risk_rating: number;
  current_risk_rating: number;
  risk_status: string;
  risk_response_strategy: string;
  planned_mitigations?: string;
  preventative_controls_status: string;
  preventative_controls_description?: string;
  detective_controls_status: string;
  detective_controls_description?: string;
  corrective_controls_status: string;
  corrective_controls_description?: string;
  control_gaps?: string;
  risk_owner: string;
  risk_owner_department: string;
  systems_affected?: string;
  technology_domain: string;
  ibs_impact: boolean;
  number_of_ibs_affected?: number;
  business_criticality: string;
  financial_impact_low?: number;
  financial_impact_high?: number;
  rto_hours?: number;
  rpo_hours?: number;
  sla_impact?: string;
  slo_impact?: string;
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
  control_posture: {
    preventative_adequate_percentage: number;
    detective_adequate_percentage: number;
    corrective_adequate_percentage: number;
    risks_with_control_gaps: number;
  };
  top_priority_risks: Array<{
    risk_id: string;
    risk_title: string;
    current_risk_rating: number;
    financial_impact_high: number | null;
    ibs_impact: boolean;
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
  impact_on_ibs: string[];
  controls_preventative: string[];
  controls_detective: string[];
  controls_corrective: string[];
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
