import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Box,
  Grid,
  Button,
  Chip,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { useRisk, useDeleteRisk } from '@/hooks/useRisks';
import { RiskLogTimeline } from '@/components/RiskLogTimeline';
import { useState } from 'react';

export const ViewRisk: React.FC = () => {
  const { riskId } = useParams<{ riskId: string }>();
  const navigate = useNavigate();
  const { data: risk, isLoading, error } = useRisk(riskId || '');
  const { mutate: deleteRisk, isPending: isDeleting } = useDeleteRisk();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleDelete = () => {
    if (riskId) {
      deleteRisk(riskId, {
        onSuccess: () => {
          navigate('/risks');
        },
      });
    }
  };

  const getRiskSeverityColor = (rating: number) => {
    if (rating >= 20) return 'error';
    if (rating >= 15) return 'warning';
    if (rating >= 10) return 'info';
    return 'success';
  };

  const getRiskSeverityLabel = (rating: number) => {
    if (rating >= 20) return 'Critical';
    if (rating >= 15) return 'High';
    if (rating >= 10) return 'Medium';
    return 'Low';
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error">
          Failed to load risk details. Please try again.
        </Alert>
      </Box>
    );
  }

  if (!risk) {
    return (
      <Box>
        <Alert severity="warning">
          Risk not found.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/risks')}
          sx={{ mr: 2 }}
        >
          Back to Risks
        </Button>
        <Typography variant="h1" sx={{ flexGrow: 1 }}>
          Risk Details
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => navigate(`/risks/${riskId}/edit`)}
          >
            Edit
          </Button>
          {!showDeleteConfirm ? (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setShowDeleteConfirm(true)}
            >
              Delete
            </Button>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="contained"
                color="error"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Confirm Delete'}
              </Button>
              <Button
                variant="outlined"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </Button>
            </Box>
          )}
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                {risk.risk_title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip label={`ID: ${risk.risk_id}`} size="small" />
                <Chip label={risk.risk_status} color="primary" size="small" />
                <Chip label={risk.risk_category} color="secondary" size="small" />
                <Chip
                  label={`${getRiskSeverityLabel(risk.current_risk_rating)} Risk`}
                  color={getRiskSeverityColor(risk.current_risk_rating)}
                  size="small"
                />
              </Box>
              <Typography variant="body1" paragraph>
                {risk.risk_description}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Assessment */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Assessment
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Inherent Risk</Typography>
                  <Typography>Probability: {risk.inherent_probability}/5</Typography>
                  <Typography>Impact: {risk.inherent_impact}/5</Typography>
                  <Typography>Rating: {risk.inherent_risk_rating}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Current Risk</Typography>
                  <Typography>Probability: {risk.current_probability}/5</Typography>
                  <Typography>Impact: {risk.current_impact}/5</Typography>
                  <Typography>Rating: {risk.current_risk_rating}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Ownership & Management */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ownership & Management
              </Typography>
              <Typography><strong>Risk Owner:</strong> {risk.risk_owner}</Typography>
              <Typography><strong>Department:</strong> {risk.risk_owner_department}</Typography>
              <Typography><strong>Technology Domain:</strong> {risk.technology_domain}</Typography>
              <Typography><strong>Business Criticality:</strong> {risk.business_criticality}</Typography>
              {risk.risk_response_strategy && (
                <Typography><strong>Response Strategy:</strong> {risk.risk_response_strategy}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Timeline */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Timeline
              </Typography>
              <Typography><strong>Date Identified:</strong> {new Date(risk.date_identified).toLocaleDateString()}</Typography>
              <Typography><strong>Last Reviewed:</strong> {new Date(risk.last_reviewed).toLocaleDateString()}</Typography>
              {risk.next_review_date && (
                <Typography><strong>Next Review:</strong> {new Date(risk.next_review_date).toLocaleDateString()}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Systems & Impact */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Systems & Business Impact
              </Typography>
              {risk.systems_affected && (
                <Typography><strong>Systems Affected:</strong> {risk.systems_affected}</Typography>
              )}
              <Typography><strong>IBS Impact:</strong> {risk.ibs_impact ? 'Yes' : 'No'}</Typography>
              {risk.ibs_impact && risk.number_of_ibs_affected && (
                <Typography><strong>IBS Affected:</strong> {risk.number_of_ibs_affected}</Typography>
              )}
              {risk.financial_impact_low && (
                <Typography><strong>Financial Impact (Low):</strong> ${risk.financial_impact_low.toLocaleString()}</Typography>
              )}
              {risk.financial_impact_high && (
                <Typography><strong>Financial Impact (High):</strong> ${risk.financial_impact_high.toLocaleString()}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Control Assessment */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Control Assessment
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">Preventative Controls</Typography>
                  <Chip
                    label={risk.preventative_controls_status}
                    color={risk.preventative_controls_status === 'Effective' ? 'success' : risk.preventative_controls_status === 'Partial' ? 'warning' : 'error'}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                  {risk.preventative_controls_description && (
                    <Typography variant="body2">{risk.preventative_controls_description}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">Detective Controls</Typography>
                  <Chip
                    label={risk.detective_controls_status}
                    color={risk.detective_controls_status === 'Effective' ? 'success' : risk.detective_controls_status === 'Partial' ? 'warning' : 'error'}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                  {risk.detective_controls_description && (
                    <Typography variant="body2">{risk.detective_controls_description}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">Corrective Controls</Typography>
                  <Chip
                    label={risk.corrective_controls_status}
                    color={risk.corrective_controls_status === 'Effective' ? 'success' : risk.corrective_controls_status === 'Partial' ? 'warning' : 'error'}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                  {risk.corrective_controls_description && (
                    <Typography variant="body2">{risk.corrective_controls_description}</Typography>
                  )}
                </Grid>
              </Grid>
              {risk.control_gaps && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2">Control Gaps</Typography>
                  <Typography variant="body2">{risk.control_gaps}</Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Mitigations & Additional Info */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Mitigations & Additional Information
              </Typography>
              {risk.planned_mitigations && (
                <>
                  <Typography variant="subtitle2">Planned Mitigations</Typography>
                  <Typography variant="body2" paragraph>{risk.planned_mitigations}</Typography>
                </>
              )}
              <Grid container spacing={2}>
                {risk.rto_hours && (
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2">RTO</Typography>
                    <Typography>{risk.rto_hours} hours</Typography>
                  </Grid>
                )}
                {risk.rpo_hours && (
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2">RPO</Typography>
                    <Typography>{risk.rpo_hours} hours</Typography>
                  </Grid>
                )}
                {risk.sla_impact && (
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2">SLA Impact</Typography>
                    <Typography>{risk.sla_impact}</Typography>
                  </Grid>
                )}
                {risk.slo_impact && (
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2">SLO Impact</Typography>
                    <Typography>{risk.slo_impact}</Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Log Timeline */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <RiskLogTimeline
                riskId={risk.risk_id}
                risk={risk}
                currentUser="Current User" // TODO: Replace with actual current user
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
