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
    previous_risk_rating: undefined as number | undefined,
    new_risk_rating: undefined as number | undefined,
    previous_probability: undefined as number | undefined,
    new_probability: undefined as number | undefined,
    previous_impact: undefined as number | undefined,
    new_impact: undefined as number | undefined,
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
        previous_risk_rating: logEntry.previous_risk_rating,
        new_risk_rating: logEntry.new_risk_rating,
        previous_probability: logEntry.previous_probability,
        new_probability: logEntry.new_probability,
        previous_impact: logEntry.previous_impact,
        new_impact: logEntry.new_impact,
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
        previous_risk_rating: undefined,
        new_risk_rating: undefined,
        previous_probability: undefined,
        new_probability: undefined,
        previous_impact: undefined,
        new_impact: undefined,
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

    // Validate risk rating changes if provided
    if (formData.new_risk_rating !== undefined) {
      if (formData.new_risk_rating < 1 || formData.new_risk_rating > 25) {
        newErrors.new_risk_rating = 'Risk rating must be between 1 and 25';
      }
    }

    if (formData.new_probability !== undefined) {
      if (formData.new_probability < 1 || formData.new_probability > 5) {
        newErrors.new_probability = 'Probability must be between 1 and 5';
      }
    }

    if (formData.new_impact !== undefined) {
      if (formData.new_impact < 1 || formData.new_impact > 5) {
        newErrors.new_impact = 'Impact must be between 1 and 5';
      }
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
        previous_risk_rating: formData.previous_risk_rating,
        new_risk_rating: formData.new_risk_rating,
        previous_probability: formData.previous_probability,
        new_probability: formData.new_probability,
        previous_impact: formData.previous_impact,
        new_impact: formData.new_impact,
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
        previous_risk_rating: formData.previous_risk_rating,
        new_risk_rating: formData.new_risk_rating,
        previous_probability: formData.previous_probability,
        new_probability: formData.new_probability,
        previous_impact: formData.previous_impact,
        new_impact: formData.new_impact,
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
      previous_risk_rating: risk.current_risk_rating,
      previous_probability: risk.current_probability,
      previous_impact: risk.current_impact,
    }));
  };

  const calculateNewRating = () => {
    if (formData.new_probability && formData.new_impact) {
      const newRating = formData.new_probability * formData.new_impact;
      setFormData(prev => ({ ...prev, new_risk_rating: newRating }));
    }
  };

  const hasRatingChange = formData.previous_risk_rating !== formData.new_risk_rating &&
                         formData.new_risk_rating !== undefined;

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

            {/* Risk Rating Changes */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Risk Rating Changes (Optional)
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
                  onClick={calculateNewRating}
                  disabled={!formData.new_probability || !formData.new_impact}
                >
                  Calculate New Rating
                </Button>
              </Box>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Previous Probability (1-5)"
                type="number"
                inputProps={{ min: 1, max: 5 }}
                value={formData.previous_probability || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  previous_probability: e.target.value ? parseInt(e.target.value) : undefined
                }))}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="New Probability (1-5)"
                type="number"
                inputProps={{ min: 1, max: 5 }}
                value={formData.new_probability || ''}
                onChange={(e) => {
                  const value = e.target.value ? parseInt(e.target.value) : undefined;
                  setFormData(prev => ({ ...prev, new_probability: value }));
                }}
                error={!!errors.new_probability}
                helperText={errors.new_probability}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Previous Impact (1-5)"
                type="number"
                inputProps={{ min: 1, max: 5 }}
                value={formData.previous_impact || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  previous_impact: e.target.value ? parseInt(e.target.value) : undefined
                }))}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="New Impact (1-5)"
                type="number"
                inputProps={{ min: 1, max: 5 }}
                value={formData.new_impact || ''}
                onChange={(e) => {
                  const value = e.target.value ? parseInt(e.target.value) : undefined;
                  setFormData(prev => ({ ...prev, new_impact: value }));
                }}
                error={!!errors.new_impact}
                helperText={errors.new_impact}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Previous Risk Rating"
                type="number"
                inputProps={{ min: 1, max: 25 }}
                value={formData.previous_risk_rating || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  previous_risk_rating: e.target.value ? parseInt(e.target.value) : undefined
                }))}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="New Risk Rating"
                type="number"
                inputProps={{ min: 1, max: 25 }}
                value={formData.new_risk_rating || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  new_risk_rating: e.target.value ? parseInt(e.target.value) : undefined
                }))}
                error={!!errors.new_risk_rating}
                helperText={errors.new_risk_rating}
              />
            </Grid>

            {hasRatingChange && (
              <Grid item xs={12}>
                <Alert severity="info">
                  Risk rating will change from {formData.previous_risk_rating} to {formData.new_risk_rating}
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
                      <Typography>Submit for approval {hasRatingChange && '(will update risk rating when approved)'}</Typography>
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
