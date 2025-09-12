// Form validation utilities for risk management

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export interface RiskFormData {
  risk_title: string;
  risk_description: string;
  risk_category: string;
  inherent_probability: number;
  inherent_impact: number;
  current_probability: number;
  current_impact: number;
  risk_status: string;
  risk_response_strategy: string;
  planned_mitigations: string;
  preventative_controls_status: string;
  preventative_controls_description: string;
  detective_controls_status: string;
  detective_controls_description: string;
  corrective_controls_status: string;
  corrective_controls_description: string;
  control_gaps: string;
  risk_owner: string;
  risk_owner_department: string;
  systems_affected: string;
  technology_domain: string;
  ibs_impact: boolean;
  number_of_ibs_affected: string;
  business_criticality: string;
  financial_impact_low: string;
  financial_impact_high: string;
  rto_hours: string;
  rpo_hours: string;
  sla_impact: string;
  slo_impact: string;
  date_identified: string;
  last_reviewed: string;
  next_review_date: string;
}

// Field length constraints based on backend model
const FIELD_CONSTRAINTS = {
  risk_title: { min: 1, max: 100 },
  risk_description: { min: 10, max: 400 },
  risk_category: { min: 1, max: 50 },
  planned_mitigations: { max: 200 },
  preventative_controls_description: { max: 150 },
  detective_controls_description: { max: 150 },
  corrective_controls_description: { max: 150 },
  control_gaps: { max: 150 },
  risk_owner: { min: 1, max: 50 },
  risk_owner_department: { min: 1, max: 50 },
  systems_affected: { max: 150 },
  technology_domain: { min: 1, max: 50 },
  sla_impact: { max: 100 },
  slo_impact: { max: 100 },
};

export const validateRiskForm = (formData: RiskFormData): ValidationResult => {
  const errors: Record<string, string> = {};

  // Required field validation
  if (!formData.risk_title.trim()) {
    errors.risk_title = 'Risk title is required';
  } else if (formData.risk_title.length > FIELD_CONSTRAINTS.risk_title.max) {
    errors.risk_title = `Risk title must not exceed ${FIELD_CONSTRAINTS.risk_title.max} characters`;
  }

  if (!formData.risk_description.trim()) {
    errors.risk_description = 'Risk description is required';
  } else if (formData.risk_description.length < FIELD_CONSTRAINTS.risk_description.min) {
    errors.risk_description = `Risk description must be at least ${FIELD_CONSTRAINTS.risk_description.min} characters`;
  } else if (formData.risk_description.length > FIELD_CONSTRAINTS.risk_description.max) {
    errors.risk_description = `Risk description must not exceed ${FIELD_CONSTRAINTS.risk_description.max} characters`;
  }

  if (!formData.risk_category.trim()) {
    errors.risk_category = 'Risk category is required';
  }

  if (!formData.technology_domain.trim()) {
    errors.technology_domain = 'Technology domain is required';
  }

  if (!formData.risk_owner.trim()) {
    errors.risk_owner = 'Risk owner is required';
  } else if (formData.risk_owner.length > FIELD_CONSTRAINTS.risk_owner.max) {
    errors.risk_owner = `Risk owner must not exceed ${FIELD_CONSTRAINTS.risk_owner.max} characters`;
  }

  if (!formData.risk_owner_department.trim()) {
    errors.risk_owner_department = 'Risk owner department is required';
  }

  if (!formData.business_criticality.trim()) {
    errors.business_criticality = 'Business criticality is required';
  }

  if (!formData.date_identified) {
    errors.date_identified = 'Date identified is required';
  }

  if (!formData.last_reviewed) {
    errors.last_reviewed = 'Last reviewed date is required';
  }

  // Probability and impact validation (1-5)
  if (formData.inherent_probability < 1 || formData.inherent_probability > 5) {
    errors.inherent_probability = 'Inherent probability must be between 1 and 5';
  }

  if (formData.inherent_impact < 1 || formData.inherent_impact > 5) {
    errors.inherent_impact = 'Inherent impact must be between 1 and 5';
  }

  if (formData.current_probability < 1 || formData.current_probability > 5) {
    errors.current_probability = 'Current probability must be between 1 and 5';
  }

  if (formData.current_impact < 1 || formData.current_impact > 5) {
    errors.current_impact = 'Current impact must be between 1 and 5';
  }

  // Date validation
  const dateIdentified = new Date(formData.date_identified);
  const lastReviewed = new Date(formData.last_reviewed);
  const today = new Date();

  if (formData.date_identified && dateIdentified > today) {
    errors.date_identified = 'Date identified cannot be in the future';
  }

  if (formData.last_reviewed && lastReviewed > today) {
    errors.last_reviewed = 'Last reviewed date cannot be in the future';
  }

  if (formData.date_identified && formData.last_reviewed && dateIdentified > lastReviewed) {
    errors.last_reviewed = 'Last reviewed date must be after the date identified';
  }

  if (formData.next_review_date) {
    const nextReview = new Date(formData.next_review_date);
    if (formData.last_reviewed && nextReview <= lastReviewed) {
      errors.next_review_date = 'Next review date must be after the last reviewed date';
    }
  }

  // Numeric field validation
  if (formData.financial_impact_low && isNaN(Number(formData.financial_impact_low))) {
    errors.financial_impact_low = 'Financial impact low must be a valid number';
  }

  if (formData.financial_impact_high && isNaN(Number(formData.financial_impact_high))) {
    errors.financial_impact_high = 'Financial impact high must be a valid number';
  }

  if (formData.financial_impact_low && formData.financial_impact_high) {
    const low = Number(formData.financial_impact_low);
    const high = Number(formData.financial_impact_high);
    if (low > high) {
      errors.financial_impact_high = 'Financial impact high must be greater than or equal to low';
    }
  }

  if (formData.rto_hours && (isNaN(Number(formData.rto_hours)) || Number(formData.rto_hours) < 0)) {
    errors.rto_hours = 'RTO hours must be a valid positive number';
  }

  if (formData.rpo_hours && (isNaN(Number(formData.rpo_hours)) || Number(formData.rpo_hours) < 0)) {
    errors.rpo_hours = 'RPO hours must be a valid positive number';
  }

  // IBS validation
  if (formData.ibs_impact && (!formData.number_of_ibs_affected || isNaN(Number(formData.number_of_ibs_affected)))) {
    errors.number_of_ibs_affected = 'Number of IBS affected is required when IBS impact is selected';
  }

  // Length constraints for optional fields
  Object.entries(FIELD_CONSTRAINTS).forEach(([field, constraint]) => {
    const value = formData[field as keyof RiskFormData] as string;
    if (value && typeof value === 'string' && 'max' in constraint && value.length > constraint.max) {
      errors[field] = `${field.replace(/_/g, ' ')} must not exceed ${constraint.max} characters`;
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Field-specific validation for real-time feedback
export const validateField = (fieldName: keyof RiskFormData, _value: unknown, formData: RiskFormData): string | null => {
  const fullValidation = validateRiskForm(formData);
  return fullValidation.errors[fieldName] || null;
};

// Format error messages for display
export const formatErrorMessage = (error: string): string => {
  return error.charAt(0).toUpperCase() + error.slice(1);
};
