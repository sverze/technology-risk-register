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

  const getNetExposureColor = (exposure: string) => {
    if (exposure.includes('Critical')) return 'error';
    if (exposure.includes('High')) return 'warning';
    if (exposure.includes('Medium')) return 'info';
    return 'success';
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
                  label={`Net Exposure: ${risk.business_disruption_net_exposure}`}
                  color={getNetExposureColor(risk.business_disruption_net_exposure)}
                  size="small"
                />
              </Box>
              <Typography variant="body1" paragraph>
                {risk.risk_description}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Business Disruption Assessment */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Business Disruption Assessment
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Impact Rating</Typography>
                <Chip
                  label={risk.business_disruption_impact_rating}
                  color={risk.business_disruption_impact_rating === 'Catastrophic' ? 'error' :
                         risk.business_disruption_impact_rating === 'Major' ? 'warning' :
                         risk.business_disruption_impact_rating === 'Moderate' ? 'info' : 'success'}
                  size="small"
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2">{risk.business_disruption_impact_description}</Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Likelihood Rating</Typography>
                <Chip
                  label={risk.business_disruption_likelihood_rating}
                  color={risk.business_disruption_likelihood_rating === 'Probable' ? 'error' :
                         risk.business_disruption_likelihood_rating === 'Possible' ? 'warning' :
                         risk.business_disruption_likelihood_rating === 'Unlikely' ? 'info' : 'success'}
                  size="small"
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2">{risk.business_disruption_likelihood_description}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2">Net Exposure</Typography>
                <Chip
                  label={risk.business_disruption_net_exposure}
                  color={getNetExposureColor(risk.business_disruption_net_exposure)}
                  size="medium"
                />
              </Box>
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

        {/* Systems & Financial Impact */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Systems & Financial Impact
              </Typography>
              {risk.systems_affected && (
                <Typography><strong>Systems Affected:</strong> {risk.systems_affected}</Typography>
              )}
              {risk.ibs_affected && (
                <Typography><strong>IBS Affected:</strong> {risk.ibs_affected}</Typography>
              )}
              {risk.financial_impact_low && (
                <Typography><strong>Financial Impact (Low):</strong> ${risk.financial_impact_low.toLocaleString()}</Typography>
              )}
              {risk.financial_impact_high && (
                <Typography><strong>Financial Impact (High):</strong> ${risk.financial_impact_high.toLocaleString()}</Typography>
              )}
              {risk.financial_impact_notes && (
                <Typography><strong>Financial Impact Notes:</strong> {risk.financial_impact_notes}</Typography>
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
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <Chip
                      label={risk.preventative_controls_coverage}
                      color={risk.preventative_controls_coverage === 'Complete Coverage' ? 'success' :
                             risk.preventative_controls_coverage === 'Incomplete Coverage' ? 'warning' :
                             risk.preventative_controls_coverage === 'No Controls' ? 'error' : 'default'}
                      size="small"
                    />
                    <Chip
                      label={risk.preventative_controls_effectiveness}
                      color={risk.preventative_controls_effectiveness === 'Fully Effective' ? 'success' :
                             risk.preventative_controls_effectiveness === 'Partially Effective' ? 'warning' : 'default'}
                      size="small"
                    />
                  </Box>
                  {risk.preventative_controls_description && (
                    <Typography variant="body2">{risk.preventative_controls_description}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">Detective Controls</Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <Chip
                      label={risk.detective_controls_coverage}
                      color={risk.detective_controls_coverage === 'Complete Coverage' ? 'success' :
                             risk.detective_controls_coverage === 'Incomplete Coverage' ? 'warning' :
                             risk.detective_controls_coverage === 'No Controls' ? 'error' : 'default'}
                      size="small"
                    />
                    <Chip
                      label={risk.detective_controls_effectiveness}
                      color={risk.detective_controls_effectiveness === 'Fully Effective' ? 'success' :
                             risk.detective_controls_effectiveness === 'Partially Effective' ? 'warning' : 'default'}
                      size="small"
                    />
                  </Box>
                  {risk.detective_controls_description && (
                    <Typography variant="body2">{risk.detective_controls_description}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2">Corrective Controls</Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <Chip
                      label={risk.corrective_controls_coverage}
                      color={risk.corrective_controls_coverage === 'Complete Coverage' ? 'success' :
                             risk.corrective_controls_coverage === 'Incomplete Coverage' ? 'warning' :
                             risk.corrective_controls_coverage === 'No Controls' ? 'error' : 'default'}
                      size="small"
                    />
                    <Chip
                      label={risk.corrective_controls_effectiveness}
                      color={risk.corrective_controls_effectiveness === 'Fully Effective' ? 'success' :
                             risk.corrective_controls_effectiveness === 'Partially Effective' ? 'warning' : 'default'}
                      size="small"
                    />
                  </Box>
                  {risk.corrective_controls_description && (
                    <Typography variant="body2">{risk.corrective_controls_description}</Typography>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Mitigations */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Mitigation Plan
              </Typography>
              {risk.planned_mitigations && (
                <>
                  <Typography variant="subtitle2">Planned Mitigations</Typography>
                  <Typography variant="body2">{risk.planned_mitigations}</Typography>
                </>
              )}
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
