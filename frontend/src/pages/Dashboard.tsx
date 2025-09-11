import { Typography, Box, Alert, CircularProgress } from '@mui/material';
import { useDashboard } from '@/hooks/useDashboard';

export const Dashboard: React.FC = () => {
  const { data: dashboardData, isLoading, error } = useDashboard();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load dashboard data. Please try again later.
      </Alert>
    );
  }

  if (!dashboardData) {
    return (
      <Alert severity="info">
        No dashboard data available.
      </Alert>
    );
  }

  const data = dashboardData;

  return (
    <Box>
      <Typography variant="h1" gutterBottom>
        Risk Dashboard
      </Typography>

      <Typography variant="h3" gutterBottom>
        Overall Risk Exposure
      </Typography>
      <Typography variant="body1">
        Total Active Risks: {data.total_active_risks}
      </Typography>
      <Typography variant="body1">
        Critical/High Priority: {data.critical_high_risk_count}
      </Typography>
      <Typography variant="body1">
        Risk Severity Distribution - Critical: {data.risk_severity_distribution.critical} |
        High: {data.risk_severity_distribution.high} |
        Medium: {data.risk_severity_distribution.medium} |
        Low: {data.risk_severity_distribution.low}
      </Typography>
      <Typography variant="body1">
        Trend Change: {data.risk_trend_change > 0 ? '+' : ''}{data.risk_trend_change.toFixed(1)}% from last month
      </Typography>

      <Typography variant="h3" gutterBottom sx={{ mt: 4 }}>
        Financial Exposure
      </Typography>
      <Typography variant="body1">
        Total Financial Exposure: ${data.total_financial_exposure.toLocaleString()}
      </Typography>
      <Typography variant="body1">
        Average Financial Impact: ${data.average_financial_impact.toLocaleString()}
      </Typography>
      <Typography variant="body1">
        High Financial Impact Risks (&gt;$1M): {data.high_financial_impact_risks}
      </Typography>

      <Typography variant="h3" gutterBottom sx={{ mt: 4 }}>
        Control Posture
      </Typography>
      <Typography variant="body1">
        Preventative Controls Adequate: {data.control_posture.preventative_adequate_percentage.toFixed(1)}%
      </Typography>
      <Typography variant="body1">
        Detective Controls Adequate: {data.control_posture.detective_adequate_percentage.toFixed(1)}%
      </Typography>
      <Typography variant="body1">
        Corrective Controls Adequate: {data.control_posture.corrective_adequate_percentage.toFixed(1)}%
      </Typography>
      <Typography variant="body1">
        Risks with Control Gaps: {data.control_posture.risks_with_control_gaps}
      </Typography>

      <Typography variant="h3" gutterBottom sx={{ mt: 4 }}>
        Top Priority Risks
      </Typography>
      {data.top_priority_risks.length > 0 ? (
        data.top_priority_risks.slice(0, 5).map((risk) => (
          <Box key={risk.risk_id} sx={{ mb: 2, p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
            <Typography variant="h6">{risk.risk_id}: {risk.risk_title}</Typography>
            <Typography variant="body2" color="text.secondary">
              Risk Rating: {risk.current_risk_rating} | Owner: {risk.risk_owner}
              {risk.financial_impact_high && ` | Financial Impact: $${risk.financial_impact_high.toLocaleString()}`}
              {risk.ibs_impact && ' | Affects IBS'}
            </Typography>
          </Box>
        ))
      ) : (
        <Typography variant="body1" color="text.secondary">
          No risks found.
        </Typography>
      )}
    </Box>
  );
};
