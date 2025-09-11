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

export const AddRisk: React.FC = () => {
  const navigate = useNavigate();
  const { mutate: createRisk, isPending, error } = useCreateRisk();
  const { data: dropdownData } = useDropdownValues();

  const [formData, setFormData] = useState({
    risk_title: '',
    risk_description: '',
    risk_category: '',
    inherent_probability: 1,
    inherent_impact: 1,
    current_probability: 1,
    current_impact: 1,
    risk_status: 'Active',
    risk_response_strategy: '',
    planned_mitigations: '',
    preventative_controls_status: 'Partial',
    preventative_controls_description: '',
    detective_controls_status: 'Partial',
    detective_controls_description: '',
    corrective_controls_status: 'Partial',
    corrective_controls_description: '',
    control_gaps: '',
    risk_owner: '',
    risk_owner_department: '',
    systems_affected: '',
    technology_domain: '',
    ibs_impact: false,
    number_of_ibs_affected: '',
    business_criticality: 'Medium',
    financial_impact_low: '',
    financial_impact_high: '',
    rto_hours: '',
    rpo_hours: '',
    sla_impact: '',
    slo_impact: '',
    date_identified: new Date().toISOString().split('T')[0],
    last_reviewed: new Date().toISOString().split('T')[0],
    next_review_date: '',
  });

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const submitData = {
      ...formData,
      financial_impact_low: formData.financial_impact_low
        ? Number(formData.financial_impact_low)
        : undefined,
      financial_impact_high: formData.financial_impact_high
        ? Number(formData.financial_impact_high)
        : undefined,
      rto_hours: formData.rto_hours
        ? Number(formData.rto_hours)
        : undefined,
      rpo_hours: formData.rpo_hours
        ? Number(formData.rpo_hours)
        : undefined,
      number_of_ibs_affected: formData.number_of_ibs_affected
        ? Number(formData.number_of_ibs_affected)
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
                label="Inherent Probability (1-5)"
                value={formData.inherent_probability}
                onChange={(e) => handleChange('inherent_probability', Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5].map((num) => (
                  <MenuItem key={num} value={num}>
                    {num}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Inherent Impact (1-5)"
                value={formData.inherent_impact}
                onChange={(e) => handleChange('inherent_impact', Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5].map((num) => (
                  <MenuItem key={num} value={num}>
                    {num}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Current Probability (1-5)"
                value={formData.current_probability}
                onChange={(e) => handleChange('current_probability', Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5].map((num) => (
                  <MenuItem key={num} value={num}>
                    {num}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Current Impact (1-5)"
                value={formData.current_impact}
                onChange={(e) => handleChange('current_impact', Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5].map((num) => (
                  <MenuItem key={num} value={num}>
                    {num}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Risk Owner"
                value={formData.risk_owner}
                onChange={(e) => handleChange('risk_owner', e.target.value)}
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
                required
                label="Business Criticality"
                value={formData.business_criticality}
                onChange={(e) => handleChange('business_criticality', e.target.value)}
              >
                <MenuItem value="Critical">Critical</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
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
                label="Next Review Date"
                value={formData.next_review_date}
                onChange={(e) => handleChange('next_review_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
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
                label="Preventative Controls Status"
                value={formData.preventative_controls_status}
                onChange={(e) => handleChange('preventative_controls_status', e.target.value)}
              >
                {dropdowns?.controls_preventative?.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Detective Controls Status"
                value={formData.detective_controls_status}
                onChange={(e) => handleChange('detective_controls_status', e.target.value)}
              >
                {dropdowns?.controls_detective?.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                required
                label="Corrective Controls Status"
                value={formData.corrective_controls_status}
                onChange={(e) => handleChange('corrective_controls_status', e.target.value)}
              >
                {dropdowns?.controls_corrective?.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Business Impact Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Business Impact Assessment
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

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="RTO (Hours)"
                value={formData.rto_hours}
                onChange={(e) => handleChange('rto_hours', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="RPO (Hours)"
                value={formData.rpo_hours}
                onChange={(e) => handleChange('rpo_hours', e.target.value)}
              />
            </Grid>

            {error && (
              <Grid item xs={12}>
                <Alert severity="error">
                  Failed to create risk. Please check your input and try again.
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
