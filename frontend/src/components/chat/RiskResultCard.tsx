import { Card, CardContent, Typography, Chip, Box, IconButton, Tooltip } from '@mui/material';
import { Visibility as ViewIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface RiskResultCardProps {
  risk: Record<string, unknown>;
}

const getNetExposureColor = (exposure: string): 'error' | 'warning' | 'info' | 'success' | 'default' => {
  if (!exposure) return 'default';
  const exposureStr = exposure.toString().toLowerCase();
  if (exposureStr.includes('critical')) return 'error';
  if (exposureStr.includes('high')) return 'warning';
  if (exposureStr.includes('medium')) return 'info';
  if (exposureStr.includes('low')) return 'success';
  return 'default';
};

export const RiskResultCard: React.FC<RiskResultCardProps> = ({ risk }) => {
  const navigate = useNavigate();

  // Extract common fields (agent might return different field names)
  const riskId = risk.risk_id || risk.id || risk.riskId;
  const title = risk.risk_title || risk.title || risk.name;
  const category = risk.risk_category || risk.category;
  const status = risk.risk_status || risk.status;
  const owner = risk.risk_owner || risk.owner;
  const exposure = risk.business_disruption_net_exposure || risk.exposure || risk.net_exposure;
  const domain = risk.technology_domain || risk.domain;

  const handleClick = () => {
    if (riskId) {
      navigate(`/risks/${riskId}`);
    }
  };

  return (
    <Card
      sx={{
        mb: 1,
        cursor: riskId ? 'pointer' : 'default',
        transition: 'all 0.2s',
        '&:hover': riskId
          ? {
              boxShadow: 3,
              transform: 'translateY(-2px)',
              borderColor: 'primary.main',
            }
          : {},
        border: '1px solid',
        borderColor: 'divider',
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            {/* Risk ID and Title */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              {riskId && (
                <Typography variant="caption" sx={{ fontFamily: 'monospace', color: 'text.secondary', fontWeight: 600 }}>
                  {riskId}
                </Typography>
              )}
              {title && (
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {title}
                </Typography>
              )}
            </Box>

            {/* Additional info chips */}
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
              {exposure && (
                <Chip
                  label={exposure}
                  color={getNetExposureColor(exposure)}
                  size="small"
                  sx={{ height: 20, fontSize: '0.7rem', fontWeight: 600 }}
                />
              )}
              {category && (
                <Chip
                  label={category}
                  variant="outlined"
                  size="small"
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              )}
              {status && (
                <Chip
                  label={status}
                  variant="outlined"
                  size="small"
                  color={status === 'Active' ? 'error' : 'default'}
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              )}
            </Box>

            {/* Owner and Domain */}
            {(owner || domain) && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                {owner && `Owner: ${owner}`}
                {owner && domain && ' • '}
                {domain && `Domain: ${domain}`}
              </Typography>
            )}
          </Box>

          {/* View button */}
          {riskId && (
            <Tooltip title="View Risk Details">
              <IconButton
                size="small"
                sx={{ color: 'primary.main' }}
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/risks/${riskId}`);
                }}
              >
                <ViewIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
