import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Box,
  Alert,
  Chip,
} from '@mui/material';
// Using native HTML date inputs instead of MUI date pickers
import { useCreateRiskLogEntry, useUpdateRiskLogEntry } from '@/hooks/useRiskLogEntries';
import type { Risk } from '@/types/risk';
import type { RiskLogEntry, RiskLogEntryCreate, RiskLogEntryUpdate, RISK_LOG_ENTRY_TYPES } from '@/types/riskLogEntry';

interface RiskLogEntryFormProps {
  open: boolean;
  onClose: () => void;
  risk: Risk;
  logEntry?: RiskLogEntry; // If provided, we're editing; otherwise creating
  currentUser: string;
}

export const RiskLogEntryForm: React.FC<RiskLogEntryFormProps> = ({
  open,
  onClose,
  risk,
  logEntry,
  currentUser,
}) => {
  const isEditing = !!logEntry;
  const { mutate: createLogEntry, isPending: isCreating } = useCreateRiskLogEntry();
  const { mutate: updateLogEntry, isPending: isUpdating } = useUpdateRiskLogEntry();

  const [formData, setFormData] = useState({
    entry_date: new Date(),
    entry_type: 'General Update' as typeof RISK_LOG_ENTRY_TYPES[number],
    entry_summary: '',
    previous_net_exposure: undefined as string | undefined,
    new_net_exposure: undefined as string | undefined,
    previous_impact_rating: undefined as string | undefined,
    new_impact_rating: undefined as string | undefined,
    previous_likelihood_rating: undefined as string | undefined,
    new_likelihood_rating: undefined as string | undefined,
    mitigation_actions_taken: '',
    risk_owner_at_time: risk.risk_owner,
    supporting_evidence: '',
    entry_status: 'Draft' as 'Draft' | 'Submitted',
    business_justification: '',
    next_review_required: undefined as Date | undefined,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Initialize form data when editing
  useEffect(() => {
    if (isEditing && logEntry) {
      setFormData({
        entry_date: new Date(logEntry.entry_date),
        entry_type: logEntry.entry_type as typeof RISK_LOG_ENTRY_TYPES[number],
        entry_summary: logEntry.entry_summary || '',
        previous_net_exposure: logEntry.previous_net_exposure,
        new_net_exposure: logEntry.new_net_exposure,
        previous_impact_rating: logEntry.previous_impact_rating,
        new_impact_rating: logEntry.new_impact_rating,
        previous_likelihood_rating: logEntry.previous_likelihood_rating,
        new_likelihood_rating: logEntry.new_likelihood_rating,
        mitigation_actions_taken: logEntry.mitigation_actions_taken || '',
        risk_owner_at_time: logEntry.risk_owner_at_time || risk.risk_owner,
        supporting_evidence: logEntry.supporting_evidence || '',
        entry_status: logEntry.entry_status as 'Draft' | 'Submitted',
        business_justification: logEntry.business_justification || '',
        next_review_required: logEntry.next_review_required ? new Date(logEntry.next_review_required) : undefined,
      });
    } else {
      // Reset form for creating new entry
      setFormData({
        entry_date: new Date(),
        entry_type: 'General Update',
        entry_summary: '',
        previous_net_exposure: undefined,
        new_net_exposure: undefined,
        previous_impact_rating: undefined,
        new_impact_rating: undefined,
        previous_likelihood_rating: undefined,
        new_likelihood_rating: undefined,
        mitigation_actions_taken: '',
        risk_owner_at_time: risk.risk_owner,
        supporting_evidence: '',
        entry_status: 'Draft',
        business_justification: '',
        next_review_required: undefined,
      });
    }
    setErrors({});
  }, [isEditing, logEntry, risk.risk_owner]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.entry_type) {
      newErrors.entry_type = 'Entry type is required';
    }
    if (!formData.entry_summary.trim()) {
      newErrors.entry_summary = 'Entry summary is required';
    }

    // Validate Business Disruption rating changes if provided
    const validImpactRatings = ['Low', 'Moderate', 'Major', 'Catastrophic'];
    const validLikelihoodRatings = ['Remote', 'Unlikely', 'Possible', 'Probable'];

    if (formData.new_impact_rating && !validImpactRatings.includes(formData.new_impact_rating)) {
      newErrors.new_impact_rating = 'Invalid impact rating';
    }

    if (formData.new_likelihood_rating && !validLikelihoodRatings.includes(formData.new_likelihood_rating)) {
      newErrors.new_likelihood_rating = 'Invalid likelihood rating';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;

    if (isEditing && logEntry) {
      const updateData: RiskLogEntryUpdate = {
        entry_date: formData.entry_date.toISOString().split('T')[0],
        entry_type: formData.entry_type,
        entry_summary: formData.entry_summary,
        previous_net_exposure: formData.previous_net_exposure,
        new_net_exposure: formData.new_net_exposure,
        previous_impact_rating: formData.previous_impact_rating,
        new_impact_rating: formData.new_impact_rating,
        previous_likelihood_rating: formData.previous_likelihood_rating,
        new_likelihood_rating: formData.new_likelihood_rating,
        mitigation_actions_taken: formData.mitigation_actions_taken || undefined,
        risk_owner_at_time: formData.risk_owner_at_time || undefined,
        supporting_evidence: formData.supporting_evidence || undefined,
        entry_status: formData.entry_status,
        business_justification: formData.business_justification || undefined,
        next_review_required: formData.next_review_required ? formData.next_review_required.toISOString().split('T')[0] : undefined,
      };

      updateLogEntry({ logEntryId: logEntry.log_entry_id, updates: updateData }, {
        onSuccess: () => {
          onClose();
        },
      });
    } else {
      const createData: RiskLogEntryCreate = {
        risk_id: risk.risk_id,
        entry_date: formData.entry_date.toISOString().split('T')[0],
        entry_type: formData.entry_type,
        entry_summary: formData.entry_summary,
        previous_net_exposure: formData.previous_net_exposure,
        new_net_exposure: formData.new_net_exposure,
        previous_impact_rating: formData.previous_impact_rating,
        new_impact_rating: formData.new_impact_rating,
        previous_likelihood_rating: formData.previous_likelihood_rating,
        new_likelihood_rating: formData.new_likelihood_rating,
        mitigation_actions_taken: formData.mitigation_actions_taken || undefined,
        risk_owner_at_time: formData.risk_owner_at_time || undefined,
        supporting_evidence: formData.supporting_evidence || undefined,
        entry_status: formData.entry_status,
        created_by: currentUser,
        business_justification: formData.business_justification || undefined,
        next_review_required: formData.next_review_required ? formData.next_review_required.toISOString().split('T')[0] : undefined,
      };

      createLogEntry(createData, {
        onSuccess: () => {
          onClose();
        },
      });
    }
  };

  const handleAutoFillCurrentRating = () => {
    setFormData(prev => ({
      ...prev,
      previous_net_exposure: risk.business_disruption_net_exposure,
      previous_impact_rating: risk.business_disruption_impact_rating,
      previous_likelihood_rating: risk.business_disruption_likelihood_rating,
    }));
  };

  const calculateNewNetExposure = () => {
    if (formData.new_impact_rating && formData.new_likelihood_rating) {
      // Map ratings to matrix values
      const impactValues = { 'Low': 1, 'Moderate': 2, 'Major': 3, 'Catastrophic': 4 };
      const likelihoodValues = { 'Remote': 1, 'Unlikely': 2, 'Possible': 3, 'Probable': 4 };

      const impactValue = impactValues[formData.new_impact_rating as keyof typeof impactValues];
      const likelihoodValue = likelihoodValues[formData.new_likelihood_rating as keyof typeof likelihoodValues];

      if (impactValue && likelihoodValue) {
        const matrixValue = impactValue * likelihoodValue;
        let exposureLevel;

        if (matrixValue >= 1 && matrixValue <= 3) exposureLevel = 'Low';
        else if (matrixValue >= 4 && matrixValue <= 6) exposureLevel = 'Medium';
        else if (matrixValue >= 8 && matrixValue <= 12) exposureLevel = 'High';
        else if (matrixValue >= 15 && matrixValue <= 16) exposureLevel = 'Critical';

        const newExposure = `${exposureLevel} (${matrixValue})`;
        setFormData(prev => ({ ...prev, new_net_exposure: newExposure }));
      }
    }
  };

  const hasRatingChange = formData.previous_net_exposure !== formData.new_net_exposure &&
                         formData.new_net_exposure !== undefined;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {isEditing ? 'Edit Log Entry' : 'Create New Log Entry'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Entry Date"
                type="date"
                value={formData.entry_date.toISOString().split('T')[0]}
                onChange={(e) => setFormData(prev => ({ ...prev, entry_date: new Date(e.target.value) }))}
                error={!!errors.entry_date}
                helperText={errors.entry_date}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!errors.entry_type}>
                <InputLabel>Entry Type</InputLabel>
                <Select
                  value={formData.entry_type}
                  label="Entry Type"
                  onChange={(e) => setFormData(prev => ({ ...prev, entry_type: e.target.value as typeof RISK_LOG_ENTRY_TYPES[number] }))}
                >
                  {(['Risk Creation', 'Risk Assessment Update', 'Mitigation Completed', 'Control Update', 'Review Completed', 'Status Change', 'Owner Change', 'General Update'] as const).map((type) => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
                {errors.entry_type && <Typography color="error" variant="caption">{errors.entry_type}</Typography>}
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Entry Summary"
                multiline
                rows={3}
                value={formData.entry_summary}
                onChange={(e) => setFormData(prev => ({ ...prev, entry_summary: e.target.value }))}
                error={!!errors.entry_summary}
                helperText={errors.entry_summary}
                required
              />
            </Grid>

            {/* Business Disruption Assessment Changes */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Business Disruption Assessment Changes (Optional)
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleAutoFillCurrentRating}
                  sx={{ mr: 2 }}
                >
                  Auto-fill Current Values
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={calculateNewNetExposure}
                  disabled={!formData.new_impact_rating || !formData.new_likelihood_rating}
                >
                  Calculate New Net Exposure
                </Button>
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Previous Impact Rating</InputLabel>
                <Select
                  value={formData.previous_impact_rating || ''}
                  label="Previous Impact Rating"
                  onChange={(e) => setFormData(prev => ({ ...prev, previous_impact_rating: e.target.value || undefined }))}
                >
                  <MenuItem value="Low">Low</MenuItem>
                  <MenuItem value="Moderate">Moderate</MenuItem>
                  <MenuItem value="Major">Major</MenuItem>
                  <MenuItem value="Catastrophic">Catastrophic</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!errors.new_impact_rating}>
                <InputLabel>New Impact Rating</InputLabel>
                <Select
                  value={formData.new_impact_rating || ''}
                  label="New Impact Rating"
                  onChange={(e) => setFormData(prev => ({ ...prev, new_impact_rating: e.target.value || undefined }))}
                >
                  <MenuItem value="Low">Low</MenuItem>
                  <MenuItem value="Moderate">Moderate</MenuItem>
                  <MenuItem value="Major">Major</MenuItem>
                  <MenuItem value="Catastrophic">Catastrophic</MenuItem>
                </Select>
                {errors.new_impact_rating && <Typography color="error" variant="caption">{errors.new_impact_rating}</Typography>}
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Previous Likelihood Rating</InputLabel>
                <Select
                  value={formData.previous_likelihood_rating || ''}
                  label="Previous Likelihood Rating"
                  onChange={(e) => setFormData(prev => ({ ...prev, previous_likelihood_rating: e.target.value || undefined }))}
                >
                  <MenuItem value="Remote">Remote</MenuItem>
                  <MenuItem value="Unlikely">Unlikely</MenuItem>
                  <MenuItem value="Possible">Possible</MenuItem>
                  <MenuItem value="Probable">Probable</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!errors.new_likelihood_rating}>
                <InputLabel>New Likelihood Rating</InputLabel>
                <Select
                  value={formData.new_likelihood_rating || ''}
                  label="New Likelihood Rating"
                  onChange={(e) => setFormData(prev => ({ ...prev, new_likelihood_rating: e.target.value || undefined }))}
                >
                  <MenuItem value="Remote">Remote</MenuItem>
                  <MenuItem value="Unlikely">Unlikely</MenuItem>
                  <MenuItem value="Possible">Possible</MenuItem>
                  <MenuItem value="Probable">Probable</MenuItem>
                </Select>
                {errors.new_likelihood_rating && <Typography color="error" variant="caption">{errors.new_likelihood_rating}</Typography>}
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Previous Net Exposure"
                value={formData.previous_net_exposure || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, previous_net_exposure: e.target.value || undefined }))}
                helperText="e.g., 'Critical (15)' or 'High (12)'"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="New Net Exposure"
                value={formData.new_net_exposure || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, new_net_exposure: e.target.value || undefined }))}
                helperText="Will be auto-calculated when using the Calculate button above"
              />
            </Grid>

            {hasRatingChange && (
              <Grid item xs={12}>
                <Alert severity="info">
                  Net exposure will change from {formData.previous_net_exposure} to {formData.new_net_exposure}
                  {formData.entry_status === 'Submitted' && ' when this entry is approved.'}
                </Alert>
              </Grid>
            )}

            {/* Additional Details */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Additional Details (Optional)
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Mitigation Actions Taken"
                multiline
                rows={3}
                value={formData.mitigation_actions_taken}
                onChange={(e) => setFormData(prev => ({ ...prev, mitigation_actions_taken: e.target.value }))}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Business Justification"
                multiline
                rows={3}
                value={formData.business_justification}
                onChange={(e) => setFormData(prev => ({ ...prev, business_justification: e.target.value }))}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Supporting Evidence"
                multiline
                rows={2}
                value={formData.supporting_evidence}
                onChange={(e) => setFormData(prev => ({ ...prev, supporting_evidence: e.target.value }))}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Risk Owner at Time of Entry"
                value={formData.risk_owner_at_time}
                onChange={(e) => setFormData(prev => ({ ...prev, risk_owner_at_time: e.target.value }))}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Next Review Required"
                type="date"
                value={formData.next_review_required ? formData.next_review_required.toISOString().split('T')[0] : ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  next_review_required: e.target.value ? new Date(e.target.value) : undefined
                }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Entry Status */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Entry Status
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Entry Status</InputLabel>
                <Select
                  value={formData.entry_status}
                  label="Entry Status"
                  onChange={(e) => setFormData(prev => ({ ...prev, entry_status: e.target.value as 'Draft' | 'Submitted' }))}
                  disabled={isEditing && logEntry?.entry_status === 'Approved'}
                >
                  <MenuItem value="Draft">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip label="Draft" size="small" />
                      <Typography>Save as draft for later completion</Typography>
                    </Box>
                  </MenuItem>
                  <MenuItem value="Submitted">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip label="Submitted" color="info" size="small" />
                      <Typography>Submit for approval {hasRatingChange && '(will update net exposure when approved)'}</Typography>
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={isCreating || isUpdating}
          >
            {isCreating || isUpdating ? 'Saving...' : isEditing ? 'Update Entry' : 'Create Entry'}
          </Button>
        </DialogActions>
      </Dialog>
  );
};
