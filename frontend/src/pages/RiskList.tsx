import React, { useState } from 'react';
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
  IconButton,
  Tooltip,
  TableSortLabel,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  FileDownload as ExportIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useRisks } from '@/hooks/useRisks';
import { useDropdownValues } from '@/hooks/useDropdownValues';
import ExcelJS from 'exceljs';

const getNetExposureColor = (exposure: string): 'error' | 'warning' | 'info' | 'success' => {
  if (exposure.includes('Critical')) return 'error';
  if (exposure.includes('High')) return 'warning';
  if (exposure.includes('Medium')) return 'info';
  return 'success';
};

const parseNetExposure = (exposure: string) => {
  // Extract level and score from "Critical (15)" format
  const match = exposure.match(/^(\w+)\s*\((\d+)\)$/);
  if (match) {
    return { level: match[1], score: parseInt(match[2]) };
  }
  return { level: exposure, score: null };
};

export const RiskList: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState('business_disruption_net_exposure');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // Column widths state for resizing
  const [columnWidths, setColumnWidths] = useState({
    risk_id: 120,
    title: 300,
    category: 120,
    rating: 140,
    status: 100,
    owner: 140,
    review: 130,
    actions: 80
  });
  
  // Resizing state
  const [isResizing, setIsResizing] = useState(false);
  const [resizingColumn, setResizingColumn] = useState<string | null>(null);
  const [startX, setStartX] = useState(0);
  const [startWidth, setStartWidth] = useState(0);

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
    setSortBy('business_disruption_net_exposure');
    setSortOrder('desc');
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const handleExportExcel = async () => {
    if (!risksData?.items || risksData.items.length === 0) {
      return;
    }

    // Prepare risks data
    const risksExportData = risksData.items.map((risk) => ({
      'Risk ID': risk.risk_id,
      'Title': risk.risk_title,
      'Description': risk.risk_description,
      'Category': risk.risk_category,
      'Status': risk.risk_status,
      'Net Exposure': risk.business_disruption_net_exposure,
      'Impact Rating': risk.business_disruption_impact_rating,
      'Impact Description': risk.business_disruption_impact_description,
      'Likelihood Rating': risk.business_disruption_likelihood_rating,
      'Likelihood Description': risk.business_disruption_likelihood_description,
      'Risk Owner': risk.risk_owner,
      'Risk Owner Department': risk.risk_owner_department,
      'Technology Domain': risk.technology_domain,
      'Risk Response Strategy': risk.risk_response_strategy,
      'Planned Mitigations': risk.planned_mitigations,
      'Preventative Controls Coverage': risk.preventative_controls_coverage,
      'Preventative Controls Effectiveness': risk.preventative_controls_effectiveness,
      'Preventative Controls Description': risk.preventative_controls_description,
      'Detective Controls Coverage': risk.detective_controls_coverage,
      'Detective Controls Effectiveness': risk.detective_controls_effectiveness,
      'Detective Controls Description': risk.detective_controls_description,
      'Corrective Controls Coverage': risk.corrective_controls_coverage,
      'Corrective Controls Effectiveness': risk.corrective_controls_effectiveness,
      'Corrective Controls Description': risk.corrective_controls_description,
      'Systems Affected': risk.systems_affected,
      'IBS Affected': risk.ibs_affected,
      'Financial Impact Low': risk.financial_impact_low,
      'Financial Impact High': risk.financial_impact_high,
      'Financial Impact Notes': risk.financial_impact_notes,
      'Date Identified': new Date(risk.date_identified).toLocaleDateString(),
      'Last Reviewed': new Date(risk.last_reviewed).toLocaleDateString(),
      'Next Review Date': risk.next_review_date ? new Date(risk.next_review_date).toLocaleDateString() : '',
      'Created At': new Date(risk.created_at).toLocaleDateString(),
      'Updated At': new Date(risk.updated_at).toLocaleDateString(),
    }));

    // Create workbook with risks sheet
    const workbook = new ExcelJS.Workbook();
    const risksWs = workbook.addWorksheet('Risks');

    // Add header row and data rows for risks
    if (risksExportData.length > 0) {
      const headers = Object.keys(risksExportData[0]);
      risksWs.addRow(headers);
      risksExportData.forEach(risk => {
        risksWs.addRow(Object.values(risk));
      });
    }

    // Try to get log entries for all risks
    try {
      const logEntriesData = [];
      for (const risk of risksData.items) {
        // Note: In a real implementation, you might want to make a single API call
        // to get all log entries at once rather than individual calls
        const response = await fetch(`/api/v1/risks/${risk.risk_id}/log-entries`);
        if (response.ok) {
          const entries = await response.json();
          for (const entry of entries) {
            logEntriesData.push({
              'Risk ID': risk.risk_id,
              'Risk Title': risk.risk_title,
              'Log Entry ID': entry.log_entry_id,
              'Entry Date': new Date(entry.entry_date).toLocaleDateString(),
              'Entry Type': entry.entry_type,
              'Entry Summary': entry.entry_summary,
              'Previous Net Exposure': entry.previous_net_exposure || '',
              'New Net Exposure': entry.new_net_exposure || '',
              'Previous Impact Rating': entry.previous_impact_rating || '',
              'New Impact Rating': entry.new_impact_rating || '',
              'Previous Likelihood Rating': entry.previous_likelihood_rating || '',
              'New Likelihood Rating': entry.new_likelihood_rating || '',
              'Mitigation Actions': entry.mitigation_actions_taken || '',
              'Risk Owner at Time': entry.risk_owner_at_time || '',
              'Supporting Evidence': entry.supporting_evidence || '',
              'Entry Status': entry.entry_status,
              'Created By': entry.created_by,
              'Reviewed By': entry.reviewed_by || '',
              'Approved Date': entry.approved_date ? new Date(entry.approved_date).toLocaleDateString() : '',
              'Business Justification': entry.business_justification || '',
              'Next Review Required': entry.next_review_required || '',
              'Created At': new Date(entry.created_at).toLocaleDateString(),
              'Updated At': new Date(entry.updated_at).toLocaleDateString(),
            });
          }
        }
      }
      
      if (logEntriesData.length > 0) {
        const logEntriesWs = workbook.addWorksheet('Risk Log Entries');
        const logHeaders = Object.keys(logEntriesData[0]);
        logEntriesWs.addRow(logHeaders);
        logEntriesData.forEach(entry => {
          logEntriesWs.addRow(Object.values(entry));
        });
      }
    } catch (error) {
      console.warn('Could not fetch log entries for export:', error);
    }

    // Download the file
    const filename = `technology-risks-export-${new Date().toISOString().split('T')[0]}.xlsx`;
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportCSV = async () => {
    if (!risksData?.items || risksData.items.length === 0) {
      return;
    }

    const risksExportData = risksData.items.map((risk) => ({
      'Risk ID': risk.risk_id,
      'Title': risk.risk_title,
      'Description': risk.risk_description,
      'Category': risk.risk_category,
      'Status': risk.risk_status,
      'Net Exposure': risk.business_disruption_net_exposure,
      'Impact Rating': risk.business_disruption_impact_rating,
      'Likelihood Rating': risk.business_disruption_likelihood_rating,
      'Risk Owner': risk.risk_owner,
      'Technology Domain': risk.technology_domain,
      'IBS Affected': risk.ibs_affected,
      'Financial Impact High': risk.financial_impact_high,
      'Date Identified': new Date(risk.date_identified).toLocaleDateString(),
      'Last Reviewed': new Date(risk.last_reviewed).toLocaleDateString(),
      'Next Review Date': risk.next_review_date ? new Date(risk.next_review_date).toLocaleDateString() : '',
    }));

    // Create workbook and worksheet for CSV export
    const workbook = new ExcelJS.Workbook();
    const ws = workbook.addWorksheet('Risks');

    // Add header row and data
    if (risksExportData.length > 0) {
      const headers = Object.keys(risksExportData[0]);
      ws.addRow(headers);
      risksExportData.forEach(risk => {
        ws.addRow(Object.values(risk));
      });
    }

    // Generate CSV from workbook
    const buffer = await workbook.csv.writeBuffer();
    const blob = new Blob([buffer], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `technology-risks-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  // Column resizing handlers
  const handleMouseDown = (e: React.MouseEvent, column: string) => {
    e.preventDefault();
    setIsResizing(true);
    setResizingColumn(column);
    setStartX(e.clientX);
    setStartWidth(columnWidths[column as keyof typeof columnWidths]);
  };
  
  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing || !resizingColumn) return;
    
    const diff = e.clientX - startX;
    const newWidth = Math.max(80, startWidth + diff); // Minimum width of 80px
    
    setColumnWidths(prev => ({
      ...prev,
      [resizingColumn]: newWidth
    }));
  };
  
  const handleMouseUp = () => {
    setIsResizing(false);
    setResizingColumn(null);
  };
  
  // Add event listeners for resizing
  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, resizingColumn, startX, startWidth]);

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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Risk List
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/risks/new')}
            sx={{ mr: 1 }}
          >
            Add Risk
          </Button>
          <Button
            variant="outlined"
            startIcon={<ExportIcon />}
            onClick={handleExportCSV}
          >
            Export CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<ExportIcon />}
            onClick={handleExportExcel}
          >
            Export Excel
          </Button>
        </Box>
      </Box>

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
              <MenuItem value="business_disruption_net_exposure">Net Exposure</MenuItem>
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

      {/* Results count and summary */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {risks.length} of {risksData?.pagination?.total || 0} risks
        </Typography>
        {risks.length > 0 && (
          <Box sx={{ display: 'flex', gap: 3 }}>
            <Typography variant="caption" color="text.secondary">
              Critical: {risks.filter(r => r.business_disruption_net_exposure?.includes('Critical')).length}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              High: {risks.filter(r => r.business_disruption_net_exposure?.includes('High')).length}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Medium: {risks.filter(r => r.business_disruption_net_exposure?.includes('Medium')).length}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Low: {risks.filter(r => r.business_disruption_net_exposure?.includes('Low')).length}
            </Typography>
          </Box>
        )}
      </Box>

      {/* Risk table */}
      <TableContainer 
        component={Paper} 
        sx={{ 
          boxShadow: 1,
          overflowX: 'auto',
          '& .resize-handle': {
            position: 'absolute',
            top: 0,
            right: 0,
            bottom: 0,
            width: '4px',
            cursor: 'col-resize',
            '&:hover': {
              backgroundColor: 'primary.main'
            }
          }
        }}
      >
        <Table sx={{ minWidth: isMobile ? 350 : isTablet ? 600 : 800, tableLayout: 'fixed' }}>
          <TableHead sx={{ backgroundColor: 'grey.50' }}>
            <TableRow>
              {/* Risk ID - Always visible */}
              <TableCell 
                sx={{ 
                  width: `${columnWidths.risk_id}px`, 
                  fontWeight: 600,
                  position: 'relative',
                  borderRight: '1px solid',
                  borderRightColor: 'divider'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <TableSortLabel
                    active={sortBy === 'risk_id'}
                    direction={sortBy === 'risk_id' ? sortOrder : 'asc'}
                    onClick={() => handleSort('risk_id')}
                  >
                    Risk ID
                  </TableSortLabel>
                  {!isMobile && (
                    <Box
                      className="resize-handle"
                      onMouseDown={(e) => handleMouseDown(e, 'risk_id')}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        bottom: 0,
                        width: '4px',
                        cursor: 'col-resize',
                        '&:hover': { backgroundColor: 'primary.main', opacity: 0.7 }
                      }}
                    />
                  )}
                </Box>
              </TableCell>
              
              {/* Title & Description - Always visible */}
              <TableCell 
                sx={{ 
                  width: `${columnWidths.title}px`, 
                  fontWeight: 600,
                  position: 'relative',
                  borderRight: '1px solid',
                  borderRightColor: 'divider'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <TableSortLabel
                    active={sortBy === 'risk_title'}
                    direction={sortBy === 'risk_title' ? sortOrder : 'asc'}
                    onClick={() => handleSort('risk_title')}
                  >
                    {isMobile ? 'Title' : 'Title & Description'}
                  </TableSortLabel>
                  {!isMobile && (
                    <Box
                      className="resize-handle"
                      onMouseDown={(e) => handleMouseDown(e, 'title')}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        bottom: 0,
                        width: '4px',
                        cursor: 'col-resize',
                        '&:hover': { backgroundColor: 'primary.main', opacity: 0.7 }
                      }}
                    />
                  )}
                </Box>
              </TableCell>
              
              {/* Category - Hide on mobile */}
              {!isMobile && (
                <TableCell 
                  sx={{ 
                    width: `${columnWidths.category}px`, 
                    fontWeight: 600,
                    position: 'relative',
                    borderRight: '1px solid',
                    borderRightColor: 'divider'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <TableSortLabel
                      active={sortBy === 'risk_category'}
                      direction={sortBy === 'risk_category' ? sortOrder : 'asc'}
                      onClick={() => handleSort('risk_category')}
                    >
                      Category
                    </TableSortLabel>
                    <Box
                      className="resize-handle"
                      onMouseDown={(e) => handleMouseDown(e, 'category')}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        bottom: 0,
                        width: '4px',
                        cursor: 'col-resize',
                        '&:hover': { backgroundColor: 'primary.main', opacity: 0.7 }
                      }}
                    />
                  </Box>
                </TableCell>
              )}
              
              {/* Net Exposure - Always visible */}
              <TableCell
                sx={{
                  width: `${columnWidths.rating}px`,
                  fontWeight: 600,
                  position: 'relative',
                  borderRight: '1px solid',
                  borderRightColor: 'divider'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <TableSortLabel
                    active={sortBy === 'business_disruption_net_exposure'}
                    direction={sortBy === 'business_disruption_net_exposure' ? sortOrder : 'asc'}
                    onClick={() => handleSort('business_disruption_net_exposure')}
                  >
                    {isMobile ? 'Exposure' : 'Net Exposure'}
                  </TableSortLabel>
                  {!isMobile && (
                    <Box
                      className="resize-handle"
                      onMouseDown={(e) => handleMouseDown(e, 'rating')}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        bottom: 0,
                        width: '4px',
                        cursor: 'col-resize',
                        '&:hover': { backgroundColor: 'primary.main', opacity: 0.7 }
                      }}
                    />
                  )}
                </Box>
              </TableCell>
              
              {/* Status - Hide on mobile */}
              {!isMobile && (
                <TableCell 
                  sx={{ 
                    width: `${columnWidths.status}px`, 
                    fontWeight: 600,
                    position: 'relative',
                    borderRight: '1px solid',
                    borderRightColor: 'divider'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <TableSortLabel
                      active={sortBy === 'risk_status'}
                      direction={sortBy === 'risk_status' ? sortOrder : 'asc'}
                      onClick={() => handleSort('risk_status')}
                    >
                      Status
                    </TableSortLabel>
                    <Box
                      className="resize-handle"
                      onMouseDown={(e) => handleMouseDown(e, 'status')}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        bottom: 0,
                        width: '4px',
                        cursor: 'col-resize',
                        '&:hover': { backgroundColor: 'primary.main', opacity: 0.7 }
                      }}
                    />
                  </Box>
                </TableCell>
              )}
              
              {/* Owner - Hide on tablet and mobile */}
              {!isTablet && (
                <TableCell 
                  sx={{ 
                    width: `${columnWidths.owner}px`, 
                    fontWeight: 600,
                    position: 'relative',
                    borderRight: '1px solid',
                    borderRightColor: 'divider'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <TableSortLabel
                      active={sortBy === 'risk_owner'}
                      direction={sortBy === 'risk_owner' ? sortOrder : 'asc'}
                      onClick={() => handleSort('risk_owner')}
                    >
                      Owner
                    </TableSortLabel>
                    <Box
                      className="resize-handle"
                      onMouseDown={(e) => handleMouseDown(e, 'owner')}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        bottom: 0,
                        width: '4px',
                        cursor: 'col-resize',
                        '&:hover': { backgroundColor: 'primary.main', opacity: 0.7 }
                      }}
                    />
                  </Box>
                </TableCell>
              )}
              
              {/* Next Review - Hide on tablet and mobile */}
              {!isTablet && (
                <TableCell 
                  sx={{ 
                    width: `${columnWidths.review}px`, 
                    fontWeight: 600,
                    position: 'relative',
                    borderRight: '1px solid',
                    borderRightColor: 'divider'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <TableSortLabel
                      active={sortBy === 'next_review_date'}
                      direction={sortBy === 'next_review_date' ? sortOrder : 'asc'}
                      onClick={() => handleSort('next_review_date')}
                    >
                      Next Review
                    </TableSortLabel>
                    <Box
                      className="resize-handle"
                      onMouseDown={(e) => handleMouseDown(e, 'review')}
                      sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        bottom: 0,
                        width: '4px',
                        cursor: 'col-resize',
                        '&:hover': { backgroundColor: 'primary.main', opacity: 0.7 }
                      }}
                    />
                  </Box>
                </TableCell>
              )}
              
              {/* Actions - Always visible */}
              <TableCell sx={{ width: `${columnWidths.actions}px`, fontWeight: 600 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {risks.length > 0 ? (
              risks.map((risk) => (
                <TableRow
                  key={risk.risk_id}
                  hover
                  sx={{ 
                    cursor: 'pointer',
                    '&:nth-of-type(odd)': { backgroundColor: 'action.hover' },
                    '&:hover': { backgroundColor: 'primary.light', color: 'primary.contrastText' }
                  }}
                  onClick={() => navigate(`/risks/${risk.risk_id}`)}
                >
                  {/* Risk ID - Always visible */}
                  <TableCell sx={{ py: 2, width: `${columnWidths.risk_id}px` }}>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 500 }}>
                      {risk.risk_id}
                    </Typography>
                  </TableCell>
                  
                  {/* Title & Description - Always visible */}
                  <TableCell sx={{ py: 2, width: `${columnWidths.title}px` }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {risk.risk_title}
                    </Typography>
                    {!isMobile && (
                      <Typography variant="body2" color="text.secondary" sx={{ 
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        fontSize: '0.875rem',
                        lineHeight: 1.2
                      }}>
                        {risk.risk_description}
                      </Typography>
                    )}
                    {isMobile && (
                      <Box sx={{ mt: 0.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          {risk.risk_category} • {risk.risk_status}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {risk.risk_owner}
                        </Typography>
                      </Box>
                    )}
                  </TableCell>
                  
                  {/* Category - Hide on mobile */}
                  {!isMobile && (
                    <TableCell sx={{ py: 2, width: `${columnWidths.category}px` }}>
                      <Typography variant="body2">{risk.risk_category}</Typography>
                    </TableCell>
                  )}
                  
                  {/* Net Exposure - Always visible */}
                  <TableCell sx={{ py: 2, width: `${columnWidths.rating}px` }}>
                    <Chip
                      label={parseNetExposure(risk.business_disruption_net_exposure).level}
                      color={getNetExposureColor(risk.business_disruption_net_exposure)}
                      size="small"
                      sx={{ minWidth: 45, fontWeight: 600 }}
                    />
                    {!isMobile && (
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                        Score: {parseNetExposure(risk.business_disruption_net_exposure).score}
                      </Typography>
                    )}
                  </TableCell>
                  
                  {/* Status - Hide on mobile */}
                  {!isMobile && (
                    <TableCell sx={{ py: 2, width: `${columnWidths.status}px` }}>
                      <Chip 
                        label={risk.risk_status} 
                        variant="outlined" 
                        size="small"
                        color={risk.risk_status === 'Active' ? 'error' : risk.risk_status === 'Monitoring' ? 'warning' : 'default'}
                      />
                    </TableCell>
                  )}
                  
                  {/* Owner - Hide on tablet and mobile */}
                  {!isTablet && (
                    <TableCell sx={{ py: 2, width: `${columnWidths.owner}px` }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {risk.risk_owner}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {risk.risk_owner_department}
                      </Typography>
                    </TableCell>
                  )}
                  
                  {/* Next Review - Hide on tablet and mobile */}
                  {!isTablet && (
                    <TableCell sx={{ py: 2, width: `${columnWidths.review}px` }}>
                      <Typography variant="body2">
                        {risk.next_review_date ? new Date(risk.next_review_date).toLocaleDateString() : 'Not set'}
                      </Typography>
                      {risk.next_review_date && new Date(risk.next_review_date) < new Date() && (
                        <Typography variant="caption" color="error.main" sx={{ display: 'block' }}>
                          Overdue
                        </Typography>
                      )}
                    </TableCell>
                  )}
                  
                  {/* Actions - Always visible */}
                  <TableCell sx={{ py: 2, width: `${columnWidths.actions}px` }}>
                    <Tooltip title="View Risk Details">
                      <IconButton 
                        size="small" 
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/risks/${risk.risk_id}`);
                        }}
                        sx={{ color: 'primary.main' }}
                      >
                        <ViewIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={isMobile ? 4 : isTablet ? 5 : 8} align="center" sx={{ py: 4 }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No risks found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {search || category || status ? 'Try adjusting your filters' : 'Get started by adding your first risk'}
                  </Typography>
                  {!search && !category && !status && (
                    <Button 
                      variant="contained" 
                      startIcon={<AddIcon />}
                      onClick={() => navigate('/risks/new')}
                      sx={{ mt: 2 }}
                    >
                      Add First Risk
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
