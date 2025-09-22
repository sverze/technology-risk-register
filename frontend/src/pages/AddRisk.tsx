import { useState } from 'react';
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useCreateRisk } from '@/hooks/useRisks';
import { useDropdownValues } from '@/hooks/useDropdownValues';
import { validateRiskForm, type RiskFormData } from '@/utils/validation';

export const AddRisk: React.FC = () => {
  const navigate = useNavigate();
  const { mutate: createRisk, isPending, error } = useCreateRisk();
  const { data: dropdownData } = useDropdownValues();
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState<RiskFormData>({
    risk_title: '',
    risk_description: '',
    risk_category: '',
    risk_status: 'Active',
    risk_response_strategy: '',
    planned_mitigations: '',

    // Control Management Fields - Updated naming
    preventative_controls_coverage: 'Not Applicable',
    preventative_controls_effectiveness: 'Not Applicable',
    preventative_controls_description: '',
    detective_controls_coverage: 'Not Applicable',
    detective_controls_effectiveness: 'Not Applicable',
    detective_controls_description: '',
    corrective_controls_coverage: 'Not Applicable',
    corrective_controls_effectiveness: 'Not Applicable',
    corrective_controls_description: '',

    // Ownership & Systems Fields
    risk_owner: '',
    risk_owner_department: '',
    systems_affected: '',
    technology_domain: '',

    // Business Disruption Assessment Fields - New model
    ibs_affected: '',
    business_disruption_impact_rating: 'Low',
    business_disruption_impact_description: '',
    business_disruption_likelihood_rating: 'Remote',
    business_disruption_likelihood_description: '',

    // Financial Impact Fields
    financial_impact_low: '',
    financial_impact_high: '',
    financial_impact_notes: '',

    // Review & Timeline Fields
    date_identified: new Date().toISOString().split('T')[0],
    last_reviewed: new Date().toISOString().split('T')[0],
    next_review_date: '',
  });

  const handleChange = (field: string, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear validation error for this field when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    const validation = validateRiskForm(formData);
    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      return;
    }

    const submitData = {
      ...formData,
      financial_impact_low: formData.financial_impact_low
        ? Number(formData.financial_impact_low)
        : undefined,
      financial_impact_high: formData.financial_impact_high
        ? Number(formData.financial_impact_high)
        : undefined,
    };

    createRisk(submitData, {
      onSuccess: () => {
        navigate('/risks');
      },
    });
  };

  const dropdowns = dropdownData;

  return (
    <Box>
      <Typography variant="h1" gutterBottom>
        Add New Risk
      </Typography>

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Risk Title"
                value={formData.risk_title}
                onChange={(e) => handleChange('risk_title', e.target.value)}
                error={!!validationErrors.risk_title}
                helperText={validationErrors.risk_title}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                multiline
                rows={4}
                label="Risk Description"
                value={formData.risk_description}
                onChange={(e) => handleChange('risk_description', e.target.value)}
                error={!!validationErrors.risk_description}
                helperText={validationErrors.risk_description}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Risk Category"
                value={formData.risk_category}
                onChange={(e) => handleChange('risk_category', e.target.value)}
              >
                {dropdowns?.categories?.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Technology Domain"
                value={formData.technology_domain}
                onChange={(e) => handleChange('technology_domain', e.target.value)}
              >
                {dropdowns?.technology_domains?.map((domain) => (
                  <MenuItem key={domain} value={domain}>
                    {domain}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Business Disruption Assessment Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Business Disruption Assessment
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Business Disruption Impact Rating"
                value={formData.business_disruption_impact_rating}
                onChange={(e) => handleChange('business_disruption_impact_rating', e.target.value)}
              >
                {dropdowns?.business_disruption_impact_ratings?.map((rating) => (
                  <MenuItem key={rating} value={rating}>
                    {rating}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Business Disruption Likelihood Rating"
                value={formData.business_disruption_likelihood_rating}
                onChange={(e) => handleChange('business_disruption_likelihood_rating', e.target.value)}
              >
                {dropdowns?.business_disruption_likelihood_ratings?.map((rating) => (
                  <MenuItem key={rating} value={rating}>
                    {rating}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                multiline
                rows={4}
                label="Business Disruption Impact Description"
                value={formData.business_disruption_impact_description}
                onChange={(e) => handleChange('business_disruption_impact_description', e.target.value)}
                error={!!validationErrors.business_disruption_impact_description}
                helperText={validationErrors.business_disruption_impact_description || 'Describe the potential business impact if this risk occurs'}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                multiline
                rows={4}
                label="Business Disruption Likelihood Description"
                value={formData.business_disruption_likelihood_description}
                onChange={(e) => handleChange('business_disruption_likelihood_description', e.target.value)}
                error={!!validationErrors.business_disruption_likelihood_description}
                helperText={validationErrors.business_disruption_likelihood_description || 'Describe the likelihood and factors that could lead to this risk occurring'}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="IBS Affected"
                value={formData.ibs_affected}
                onChange={(e) => handleChange('ibs_affected', e.target.value)}
                helperText="List the Important Business Services that would be affected by this risk"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Risk Owner"
                value={formData.risk_owner}
                onChange={(e) => handleChange('risk_owner', e.target.value)}
                error={!!validationErrors.risk_owner}
                helperText={validationErrors.risk_owner}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Risk Owner Department"
                value={formData.risk_owner_department}
                onChange={(e) => handleChange('risk_owner_department', e.target.value)}
              >
                {dropdowns?.departments?.map((dept) => (
                  <MenuItem key={dept} value={dept}>
                    {dept}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>


            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Risk Response Strategy"
                value={formData.risk_response_strategy}
                onChange={(e) => handleChange('risk_response_strategy', e.target.value)}
              >
                {dropdowns?.risk_response_strategies?.map((strategy) => (
                  <MenuItem key={strategy} value={strategy}>
                    {strategy}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Risk Status"
                value={formData.risk_status}
                onChange={(e) => handleChange('risk_status', e.target.value)}
              >
                {dropdowns?.statuses?.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                required
                label="Date Identified"
                value={formData.date_identified}
                onChange={(e) => handleChange('date_identified', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                required
                label="Last Reviewed"
                value={formData.last_reviewed}
                onChange={(e) => handleChange('last_reviewed', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Next Review Date"
                value={formData.next_review_date}
                onChange={(e) => handleChange('next_review_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Planned Mitigations"
                value={formData.planned_mitigations}
                onChange={(e) => handleChange('planned_mitigations', e.target.value)}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Systems Affected"
                value={formData.systems_affected}
                onChange={(e) => handleChange('systems_affected', e.target.value)}
              />
            </Grid>

            {/* Controls Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Control Assessment
              </Typography>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Preventative Controls Coverage"
                value={formData.preventative_controls_coverage}
                onChange={(e) => handleChange('preventative_controls_coverage', e.target.value)}
              >
                {dropdowns?.controls_coverage?.map((coverage) => (
                  <MenuItem key={coverage} value={coverage}>
                    {coverage}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Detective Controls Coverage"
                value={formData.detective_controls_coverage}
                onChange={(e) => handleChange('detective_controls_coverage', e.target.value)}
              >
                {dropdowns?.controls_coverage?.map((coverage) => (
                  <MenuItem key={coverage} value={coverage}>
                    {coverage}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Corrective Controls Coverage"
                value={formData.corrective_controls_coverage}
                onChange={(e) => handleChange('corrective_controls_coverage', e.target.value)}
              >
                {dropdowns?.controls_coverage?.map((coverage) => (
                  <MenuItem key={coverage} value={coverage}>
                    {coverage}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Preventative Controls Effectiveness"
                value={formData.preventative_controls_effectiveness}
                onChange={(e) => handleChange('preventative_controls_effectiveness', e.target.value)}
              >
                {dropdowns?.controls_effectiveness?.map((effectiveness) => (
                  <MenuItem key={effectiveness} value={effectiveness}>
                    {effectiveness}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Detective Controls Effectiveness"
                value={formData.detective_controls_effectiveness}
                onChange={(e) => handleChange('detective_controls_effectiveness', e.target.value)}
              >
                {dropdowns?.controls_effectiveness?.map((effectiveness) => (
                  <MenuItem key={effectiveness} value={effectiveness}>
                    {effectiveness}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Corrective Controls Effectiveness"
                value={formData.corrective_controls_effectiveness}
                onChange={(e) => handleChange('corrective_controls_effectiveness', e.target.value)}
              >
                {dropdowns?.controls_effectiveness?.map((effectiveness) => (
                  <MenuItem key={effectiveness} value={effectiveness}>
                    {effectiveness}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Preventative Controls Description"
                value={formData.preventative_controls_description}
                onChange={(e) => handleChange('preventative_controls_description', e.target.value)}
                helperText="Describe preventative controls in place to reduce likelihood of occurrence"
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Detective Controls Description"
                value={formData.detective_controls_description}
                onChange={(e) => handleChange('detective_controls_description', e.target.value)}
                helperText="Describe detective controls in place to identify when risk occurs"
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Corrective Controls Description"
                value={formData.corrective_controls_description}
                onChange={(e) => handleChange('corrective_controls_description', e.target.value)}
                helperText="Describe corrective controls in place to mitigate impact when risk occurs"
              />
            </Grid>

            {/* Financial Impact Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Financial Impact Assessment
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Financial Impact Low ($)"
                value={formData.financial_impact_low}
                onChange={(e) => handleChange('financial_impact_low', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Financial Impact High ($)"
                value={formData.financial_impact_high}
                onChange={(e) => handleChange('financial_impact_high', e.target.value)}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Financial Impact Notes"
                value={formData.financial_impact_notes}
                onChange={(e) => handleChange('financial_impact_notes', e.target.value)}
                helperText="Additional context for the financial impact estimates (e.g., calculation method, assumptions)"
              />
            </Grid>

            {error && (
              <Grid item xs={12}>
                <Alert severity="error">
                  Failed to create risk. Please check your input and try again.
                </Alert>
              </Grid>
            )}

            {Object.keys(validationErrors).length > 0 && (
              <Grid item xs={12}>
                <Alert severity="warning">
                  Please correct the highlighted fields above before submitting.
                </Alert>
              </Grid>
            )}

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={isPending}
                  startIcon={isPending ? <CircularProgress size={20} /> : null}
                >
                  {isPending ? 'Creating...' : 'Create Risk'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/risks')}
                >
                  Cancel
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
};
