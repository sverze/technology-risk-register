import {
  Typography,
  Box,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
  BusinessCenter,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
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

  // Helper functions
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };


  const getDomainRiskColor = (avgRating: number) => {
    if (avgRating >= 16) return 'error';
    if (avgRating >= 12) return 'warning';
    if (avgRating >= 6) return 'info';
    return 'success';
  };

  // Prepare chart data
  const severityChartData = [
    { name: 'Critical (16-25)', count: data.risk_severity_distribution.critical, color: '#f44336' },
    { name: 'High (12-15)', count: data.risk_severity_distribution.high, color: '#ff9800' },
    { name: 'Medium (6-11)', count: data.risk_severity_distribution.medium, color: '#2196f3' },
    { name: 'Low (1-5)', count: data.risk_severity_distribution.low, color: '#4caf50' },
  ];

  const responseStrategyData = [
    { name: 'Mitigate', value: data.risk_response_breakdown.mitigate, color: '#2196f3' },
    { name: 'Accept', value: data.risk_response_breakdown.accept, color: '#ff9800' },
    { name: 'Transfer', value: data.risk_response_breakdown.transfer, color: '#9c27b0' },
    { name: 'Avoid', value: data.risk_response_breakdown.avoid, color: '#4caf50' },
  ];

  const getActivityStatus = () => {
    const { overdue_reviews, risks_reviewed_this_month } = data.risk_management_activity;
    if (overdue_reviews > 5) return { color: 'error', icon: <Error />, text: 'Attention Needed' };
    if (overdue_reviews > 0 || risks_reviewed_this_month < 5) return { color: 'warning', icon: <Warning />, text: 'Monitor' };
    return { color: 'success', icon: <CheckCircle />, text: 'On Track' };
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
        Technology Risk Dashboard
      </Typography>

      {/* Executive Summary Section */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2, color: 'primary.main' }}>
        Executive Summary
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Overall Risk Exposure */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Risk Exposure
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h3" sx={{ mr: 1 }}>
                  {data.total_active_risks}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Active Risks
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="h4" color="error.main" sx={{ mr: 1 }}>
                  {data.critical_high_risk_count}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Critical/High
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {data.risk_trend_change >= 0 ? (
                  <TrendingUp color="error" sx={{ mr: 0.5 }} />
                ) : (
                  <TrendingDown color="success" sx={{ mr: 0.5 }} />
                )}
                <Typography variant="body2">
                  {data.risk_trend_change >= 0 ? '+' : ''}{data.risk_trend_change.toFixed(1)}% from last month
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Financial Impact Exposure */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Impact Exposure
              </Typography>
              <Typography variant="h4" color="primary.main" gutterBottom>
                {formatCurrency(Number(data.total_financial_exposure))}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Total Estimated Exposure
              </Typography>
              <Typography variant="body1">
                Avg per Risk: {formatCurrency(Number(data.average_financial_impact))}
              </Typography>
              <Typography variant="body1">
                High Impact Risks (&gt;$1M): {data.high_financial_impact_risks}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Business Service Risk Exposure */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Business Service Exposure
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <BusinessCenter sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h4">
                  {data.business_service_exposure.risks_affecting_ibs}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Risks Affecting Business Services
              </Typography>
              <Typography variant="body1">
                Total IBS Affected: {data.business_service_exposure.total_ibs_affected}
              </Typography>
              <Typography variant="body1">
                Critical IBS Risks: {data.business_service_exposure.critical_risks_affecting_ibs}
              </Typography>
              <Typography variant="body2" color="primary.main">
                {data.business_service_exposure.percentage_risks_with_ibs_impact.toFixed(1)}% of all risks
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Distribution Analysis Section */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2, color: 'primary.main' }}>
        Distribution Analysis
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Risk Distribution by Severity */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '400px' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution by Severity
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={severityChartData} margin={{ top: 20, right: 30, left: 20, bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    angle={-45} 
                    textAnchor="end" 
                    height={50}
                    interval={0}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count">
                    {severityChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Response Strategy Breakdown */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '400px' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Response Strategy
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={responseStrategyData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: any) => `${entry.name} ${(entry.percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {responseStrategyData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Technology Domain Risk Table */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk by Technology Domain
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Domain</TableCell>
                      <TableCell align="right">Risk Count</TableCell>
                      <TableCell align="right">Avg Risk Rating</TableCell>
                      <TableCell align="right">Risk Level</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.technology_domain_risks.map((domain) => (
                      <TableRow key={domain.domain}>
                        <TableCell component="th" scope="row">
                          {domain.domain}
                        </TableCell>
                        <TableCell align="right">{domain.risk_count}</TableCell>
                        <TableCell align="right">{domain.average_risk_rating.toFixed(1)}</TableCell>
                        <TableCell align="right">
                          <Chip
                            size="small"
                            color={getDomainRiskColor(domain.average_risk_rating)}
                            label={
                              domain.average_risk_rating >= 16 ? 'Critical' :
                              domain.average_risk_rating >= 12 ? 'High' :
                              domain.average_risk_rating >= 6 ? 'Medium' : 'Low'
                            }
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Control Posture Overview */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Control Posture Overview
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Preventative Controls
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={data.control_posture.preventative_adequate_percentage}
                  sx={{ height: 8, borderRadius: 4, mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {data.control_posture.preventative_adequate_percentage.toFixed(1)}% Adequate
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Detective Controls
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={data.control_posture.detective_adequate_percentage}
                  color="secondary"
                  sx={{ height: 8, borderRadius: 4, mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {data.control_posture.detective_adequate_percentage.toFixed(1)}% Adequate
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Corrective Controls
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={data.control_posture.corrective_adequate_percentage}
                  color="info"
                  sx={{ height: 8, borderRadius: 4, mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {data.control_posture.corrective_adequate_percentage.toFixed(1)}% Adequate
                </Typography>
              </Box>
              <Box sx={{ p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
                <Typography variant="body2" color="error.contrastText">
                  {data.control_posture.risks_with_control_gaps} risks with control gaps
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action-Oriented Detail Section */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2, color: 'primary.main' }}>
        Action Required
      </Typography>
      <Grid container spacing={3}>
        {/* Top 10 Highest Priority Risks */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top 10 Highest Priority Risks
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Risk ID</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell align="right">Rating</TableCell>
                      <TableCell align="right">Financial Impact</TableCell>
                      <TableCell>IBS</TableCell>
                      <TableCell>Owner</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.top_priority_risks.map((risk) => (
                      <TableRow key={risk.risk_id}>
                        <TableCell component="th" scope="row">
                          {risk.risk_id}
                        </TableCell>
                        <TableCell>{risk.risk_title}</TableCell>
                        <TableCell align="right">
                          <Chip
                            size="small"
                            color={risk.current_risk_rating >= 16 ? 'error' : risk.current_risk_rating >= 12 ? 'warning' : 'info'}
                            label={risk.current_risk_rating}
                          />
                        </TableCell>
                        <TableCell align="right">
                          {risk.financial_impact_high ? formatCurrency(Number(risk.financial_impact_high)) : '-'}
                        </TableCell>
                        <TableCell>
                          {risk.ibs_impact ? <Warning color="warning" /> : ''}
                        </TableCell>
                        <TableCell>{risk.risk_owner}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Management Activity */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Management Activity
              </Typography>
              
              {/* Overall Status Banner */}
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 3, 
                p: 2, 
                borderRadius: 2,
                bgcolor: `${getActivityStatus().color}.light`,
                border: `2px solid`,
                borderColor: `${getActivityStatus().color}.main`
              }}>
                {getActivityStatus().icon}
                <Typography variant="h6" sx={{ ml: 1, color: `${getActivityStatus().color}.contrastText` }}>
                  {getActivityStatus().text}
                </Typography>
              </Box>

              {/* Activity Metrics with Visual Indicators */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Reviews This Month
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CheckCircle 
                      color={data.risk_management_activity.risks_reviewed_this_month >= 5 ? 'success' : 'disabled'} 
                      sx={{ mr: 1 }} 
                    />
                    <Typography variant="h5" color="primary.main">
                      {data.risk_management_activity.risks_reviewed_this_month}
                    </Typography>
                  </Box>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min((data.risk_management_activity.risks_reviewed_this_month / 10) * 100, 100)}
                  sx={{ height: 6, borderRadius: 3, mb: 1 }}
                />
                <Typography variant="caption" color="text.secondary">
                  Target: 10 reviews/month
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Overdue Reviews
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {data.risk_management_activity.overdue_reviews > 0 ? (
                      <Warning color="error" sx={{ mr: 1 }} />
                    ) : (
                      <CheckCircle color="success" sx={{ mr: 1 }} />
                    )}
                    <Typography 
                      variant="h5" 
                      color={data.risk_management_activity.overdue_reviews > 0 ? 'error.main' : 'success.main'}
                    >
                      {data.risk_management_activity.overdue_reviews}
                    </Typography>
                  </Box>
                </Box>
                {data.risk_management_activity.overdue_reviews > 0 && (
                  <Box sx={{ p: 1.5, bgcolor: 'error.light', borderRadius: 1 }}>
                    <Typography variant="caption" color="error.contrastText">
                      ⚠️ {data.risk_management_activity.overdue_reviews} risk{data.risk_management_activity.overdue_reviews > 1 ? 's' : ''} need immediate review
                    </Typography>
                  </Box>
                )}
              </Box>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Recent Changes (30 days)
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <BusinessCenter color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h5" color="primary.main">
                      {data.risk_management_activity.recent_risk_rating_changes}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Risk assessment updates and rating changes
                </Typography>
              </Box>

              {/* Action Items */}
              <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Next Actions
                </Typography>
                {data.risk_management_activity.overdue_reviews > 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    • Review {data.risk_management_activity.overdue_reviews} overdue risk{data.risk_management_activity.overdue_reviews > 1 ? 's' : ''}
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    • All reviews are up to date ✓
                  </Typography>
                )}
                {data.risk_management_activity.risks_reviewed_this_month < 5 && (
                  <Typography variant="body2" color="text.secondary">
                    • Schedule more risk reviews this month
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
