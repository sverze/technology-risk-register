// Form validation utilities for risk management

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export interface RiskFormData {
  risk_title: string;
  risk_description: string;
  risk_category: string;
  risk_status: string;
  risk_response_strategy: string;
  planned_mitigations: string;

  // Control Management Fields - Updated naming
  preventative_controls_coverage: string;
  preventative_controls_effectiveness: string;
  preventative_controls_description: string;
  detective_controls_coverage: string;
  detective_controls_effectiveness: string;
  detective_controls_description: string;
  corrective_controls_coverage: string;
  corrective_controls_effectiveness: string;
  corrective_controls_description: string;

  // Ownership & Systems Fields
  risk_owner: string;
  risk_owner_department: string;
  systems_affected: string;
  technology_domain: string;

  // Business Disruption Assessment Fields - New model
  ibs_affected: string;
  business_disruption_impact_rating: string;
  business_disruption_impact_description: string;
  business_disruption_likelihood_rating: string;
  business_disruption_likelihood_description: string;

  // Financial Impact Fields
  financial_impact_low: string;
  financial_impact_high: string;
  financial_impact_notes: string;

  // Review & Timeline Fields
  date_identified: string;
  last_reviewed: string;
  next_review_date: string;
}

// Field length constraints based on backend model
const FIELD_CONSTRAINTS = {
  risk_title: { min: 1, max: 100 },
  risk_description: { min: 10, max: 500 },
  risk_category: { min: 1, max: 50 },
  planned_mitigations: { max: 200 },
  preventative_controls_description: { max: 500 },
  detective_controls_description: { max: 500 },
  corrective_controls_description: { max: 500 },
  risk_owner: { min: 1, max: 50 },
  risk_owner_department: { min: 1, max: 50 },
  systems_affected: { max: 150 },
  technology_domain: { min: 1, max: 50 },
  business_disruption_impact_description: { min: 10, max: 400 },
  business_disruption_likelihood_description: { min: 10, max: 400 },
  financial_impact_notes: { max: 200 },
  ibs_affected: { max: 200 },
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

  if (!formData.business_disruption_impact_rating.trim()) {
    errors.business_disruption_impact_rating = 'Business Disruption Impact Rating is required';
  }

  if (!formData.business_disruption_likelihood_rating.trim()) {
    errors.business_disruption_likelihood_rating = 'Business Disruption Likelihood Rating is required';
  }

  if (!formData.business_disruption_impact_description.trim()) {
    errors.business_disruption_impact_description = 'Business Disruption Impact Description is required';
  } else if (formData.business_disruption_impact_description.length < FIELD_CONSTRAINTS.business_disruption_impact_description.min) {
    errors.business_disruption_impact_description = `Impact description must be at least ${FIELD_CONSTRAINTS.business_disruption_impact_description.min} characters`;
  } else if (formData.business_disruption_impact_description.length > FIELD_CONSTRAINTS.business_disruption_impact_description.max) {
    errors.business_disruption_impact_description = `Impact description must not exceed ${FIELD_CONSTRAINTS.business_disruption_impact_description.max} characters`;
  }

  if (!formData.business_disruption_likelihood_description.trim()) {
    errors.business_disruption_likelihood_description = 'Business Disruption Likelihood Description is required';
  } else if (formData.business_disruption_likelihood_description.length < FIELD_CONSTRAINTS.business_disruption_likelihood_description.min) {
    errors.business_disruption_likelihood_description = `Likelihood description must be at least ${FIELD_CONSTRAINTS.business_disruption_likelihood_description.min} characters`;
  } else if (formData.business_disruption_likelihood_description.length > FIELD_CONSTRAINTS.business_disruption_likelihood_description.max) {
    errors.business_disruption_likelihood_description = `Likelihood description must not exceed ${FIELD_CONSTRAINTS.business_disruption_likelihood_description.max} characters`;
  }

  if (!formData.date_identified) {
    errors.date_identified = 'Date identified is required';
  }

  if (!formData.last_reviewed) {
    errors.last_reviewed = 'Last reviewed date is required';
  }

  // Control coverage and effectiveness validation
  if (!formData.preventative_controls_coverage.trim()) {
    errors.preventative_controls_coverage = 'Preventative controls coverage is required';
  }

  if (!formData.preventative_controls_effectiveness.trim()) {
    errors.preventative_controls_effectiveness = 'Preventative controls effectiveness is required';
  }

  if (!formData.detective_controls_coverage.trim()) {
    errors.detective_controls_coverage = 'Detective controls coverage is required';
  }

  if (!formData.detective_controls_effectiveness.trim()) {
    errors.detective_controls_effectiveness = 'Detective controls effectiveness is required';
  }

  if (!formData.corrective_controls_coverage.trim()) {
    errors.corrective_controls_coverage = 'Corrective controls coverage is required';
  }

  if (!formData.corrective_controls_effectiveness.trim()) {
    errors.corrective_controls_effectiveness = 'Corrective controls effectiveness is required';
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

  // RTO/RPO fields removed from Business Disruption model

  // IBS validation - now a text field
  // No specific validation needed for ibs_affected as it's optional text

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
