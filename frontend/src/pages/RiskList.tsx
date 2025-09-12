import { useState } from 'react';
import {
  Typography,
  Box,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  Grid,
  MenuItem,
  Button,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useRisks } from '@/hooks/useRisks';
import { useDropdownValues } from '@/hooks/useDropdownValues';

const getSeverityColor = (rating: number): 'error' | 'warning' | 'info' | 'success' => {
  if (rating >= 20) return 'error';
  if (rating >= 15) return 'warning';
  if (rating >= 10) return 'info';
  return 'success';
};

const getSeverityLabel = (rating: number): string => {
  if (rating >= 20) return 'Critical';
  if (rating >= 15) return 'High';
  if (rating >= 10) return 'Medium';
  return 'Low';
};

export const RiskList: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState('current_risk_rating');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const { data: risksData, isLoading, error } = useRisks({
    search: search || undefined,
    category: category || undefined,
    status: status || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    limit: 50,
  });

  const { data: dropdownData } = useDropdownValues();

  const handleClearFilters = () => {
    setSearch('');
    setCategory('');
    setStatus('');
    setSortBy('current_risk_rating');
    setSortOrder('desc');
  };

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
        Failed to load risks. Please try again later.
      </Alert>
    );
  }

  const risks = risksData?.items || [];
  const categories = dropdownData?.categories || [];
  const statuses = dropdownData?.statuses || [];

  return (
    <Box>
      <Typography variant="h1" gutterBottom>
        Risk List
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search risks..."
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              select
              fullWidth
              label="Category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map((cat) => (
                <MenuItem key={cat} value={cat}>
                  {cat}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              select
              fullWidth
              label="Status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Statuses</MenuItem>
              {statuses.map((stat) => (
                <MenuItem key={stat} value={stat}>
                  {stat}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              select
              fullWidth
              label="Sort By"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              size="small"
            >
              <MenuItem value="current_risk_rating">Risk Rating</MenuItem>
              <MenuItem value="risk_title">Title</MenuItem>
              <MenuItem value="risk_category">Category</MenuItem>
              <MenuItem value="risk_status">Status</MenuItem>
              <MenuItem value="created_at">Created Date</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={1}>
            <TextField
              select
              fullWidth
              label="Order"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
              size="small"
            >
              <MenuItem value="desc">Desc</MenuItem>
              <MenuItem value="asc">Asc</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Button onClick={handleClearFilters} variant="outlined" fullWidth>
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Results count */}
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Showing {risks.length} of {risksData?.pagination?.total || 0} risks
      </Typography>

      {/* Risk table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Risk ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Risk Rating</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Next Review</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {risks.length > 0 ? (
              risks.map((risk) => (
                <TableRow
                  key={risk.risk_id}
                  hover
                  onClick={() => navigate(`/risks/${risk.risk_id}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{risk.risk_id}</TableCell>
                  <TableCell>
                    <Typography variant="subtitle2">{risk.risk_title}</Typography>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      {risk.risk_description.length > 100
                        ? `${risk.risk_description.substring(0, 100)}...`
                        : risk.risk_description}
                    </Typography>
                  </TableCell>
                  <TableCell>{risk.risk_category}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${risk.current_risk_rating} (${getSeverityLabel(risk.current_risk_rating)})`}
                      color={getSeverityColor(risk.current_risk_rating)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label={risk.risk_status} variant="outlined" size="small" />
                  </TableCell>
                  <TableCell>{risk.risk_owner}</TableCell>
                  <TableCell>
                    {new Date(risk.next_review_date).toLocaleDateString()}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body1" color="text.secondary">
                    No risks found matching your criteria.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
