import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Button,
  Divider,
  Grid,
  Alert,
  Collapse,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Check as ApproveIcon,
  Close as RejectIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { useRiskLogEntries, useApproveRiskLogEntry, useRejectRiskLogEntry, useDeleteRiskLogEntry } from '@/hooks/useRiskLogEntries';
import { RiskLogEntryForm } from './RiskLogEntryForm';
import type { RiskLogEntry, RiskLogEntryStatus } from '@/types/riskLogEntry';
import type { Risk } from '@/types/risk';

interface RiskLogTimelineProps {
  riskId: string;
  risk: Risk;
  currentUser?: string;
}

export const RiskLogTimeline: React.FC<RiskLogTimelineProps> = ({
  riskId,
  risk,
  currentUser = 'Current User',
}) => {
  const { data: logEntries, isLoading, error } = useRiskLogEntries(riskId);
  const { mutate: approveEntry, isPending: isApproving } = useApproveRiskLogEntry();
  const { mutate: rejectEntry, isPending: isRejecting } = useRejectRiskLogEntry();
  const { mutate: deleteEntry } = useDeleteRiskLogEntry();

  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set());
  const [menuAnchor, setMenuAnchor] = useState<{ element: HTMLElement; entryId: string } | null>(null);
  const [approvalDialog, setApprovalDialog] = useState<{ isOpen: boolean; entry: RiskLogEntry | null; action: 'approve' | 'reject' }>({
    isOpen: false,
    entry: null,
    action: 'approve',
  });
  const [formDialog, setFormDialog] = useState<{ isOpen: boolean; editingEntry: RiskLogEntry | null }>({
    isOpen: false,
    editingEntry: null,
  });


  const toggleExpanded = (entryId: string) => {
    const newExpanded = new Set(expandedEntries);
    if (newExpanded.has(entryId)) {
      newExpanded.delete(entryId);
    } else {
      newExpanded.add(entryId);
    }
    setExpandedEntries(newExpanded);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, entryId: string) => {
    setMenuAnchor({ element: event.currentTarget, entryId });
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const handleEdit = (logEntry: RiskLogEntry) => {
    handleMenuClose();
    setFormDialog({ isOpen: true, editingEntry: logEntry });
  };

  const handleCreate = () => {
    setFormDialog({ isOpen: true, editingEntry: null });
  };

  const handleFormClose = () => {
    setFormDialog({ isOpen: false, editingEntry: null });
  };

  const handleDelete = (entryId: string) => {
    handleMenuClose();
    deleteEntry(entryId);
  };

  const handleApprovalAction = (entry: RiskLogEntry, action: 'approve' | 'reject') => {
    handleMenuClose();
    setApprovalDialog({ isOpen: true, entry, action });
  };

  const executeApprovalAction = () => {
    if (!approvalDialog.entry) return;

    if (approvalDialog.action === 'approve') {
      approveEntry({
        logEntryId: approvalDialog.entry.log_entry_id,
        reviewedBy: currentUser
      });
    } else {
      rejectEntry({
        logEntryId: approvalDialog.entry.log_entry_id,
        reviewedBy: currentUser
      });
    }

    setApprovalDialog({ isOpen: false, entry: null, action: 'approve' });
  };

  const getStatusColor = (status: RiskLogEntryStatus) => {
    switch (status) {
      case 'Draft': return 'default';
      case 'Submitted': return 'info';
      case 'Approved': return 'success';
      case 'Rejected': return 'error';
      default: return 'default';
    }
  };



  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <Typography>Loading log entries...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load log entries. Please try again.
      </Alert>
    );
  }

  if (!logEntries || logEntries.length === 0) {
    return (
      <>
        <Box textAlign="center" p={3}>
          <TimelineIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Log Entries Yet
          </Typography>
          <Typography color="text.secondary" paragraph>
            This risk doesn't have any log entries yet. Create the first entry to start tracking changes and updates.
          </Typography>
          <Button variant="contained" onClick={handleCreate}>
            Create First Log Entry
          </Button>
        </Box>

        {/* Create/Edit Form Dialog - Always rendered */}
        <RiskLogEntryForm
          open={formDialog.isOpen}
          onClose={handleFormClose}
          risk={risk}
          logEntry={formDialog.editingEntry || undefined}
          currentUser={currentUser}
        />
      </>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Risk Log Timeline ({logEntries.length} entries)
        </Typography>
        <Button variant="contained" onClick={handleCreate} size="small">
          Add Log Entry
        </Button>
      </Box>

      <Box sx={{ position: 'relative' }}>
        {/* Timeline line */}
        <Box
          sx={{
            position: 'absolute',
            left: 16,
            top: 0,
            bottom: 0,
            width: 2,
            bgcolor: 'divider',
            zIndex: 0,
          }}
        />

        {logEntries.map((entry) => {
          const isExpanded = expandedEntries.has(entry.log_entry_id);
          const hasRatingChange = entry.previous_net_exposure !== entry.new_net_exposure;

          return (
            <Box key={entry.log_entry_id} sx={{ position: 'relative', mb: 2 }}>
              {/* Timeline dot */}
              <Box
                sx={{
                  position: 'absolute',
                  left: 8,
                  top: 16,
                  width: 16,
                  height: 16,
                  borderRadius: '50%',
                  bgcolor: getStatusColor(entry.entry_status as RiskLogEntryStatus) === 'success' ? 'success.main' :
                           getStatusColor(entry.entry_status as RiskLogEntryStatus) === 'error' ? 'error.main' :
                           getStatusColor(entry.entry_status as RiskLogEntryStatus) === 'info' ? 'info.main' : 'grey.400',
                  border: 2,
                  borderColor: 'background.paper',
                  zIndex: 1,
                }}
              />

              <Card sx={{ ml: 4, position: 'relative' }}>
                <CardContent sx={{ pb: 1 }}>
                  {/* Header */}
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                    <Box flex={1}>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip
                          label={entry.entry_status}
                          color={getStatusColor(entry.entry_status as RiskLogEntryStatus)}
                          size="small"
                        />
                        <Typography variant="body2" color="text.secondary">
                          {new Date(entry.entry_date).toLocaleDateString()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          by {entry.created_by}
                        </Typography>
                      </Box>
                      <Typography variant="subtitle1" fontWeight="medium">
                        {entry.entry_type}
                      </Typography>
                    </Box>

                    <Box display="flex" alignItems="center">
                      <IconButton
                        size="small"
                        onClick={() => toggleExpanded(entry.log_entry_id)}
                      >
                        {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, entry.log_entry_id)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </Box>
                  </Box>

                  {/* Summary */}
                  <Typography variant="body2" paragraph>
                    {entry.entry_summary}
                  </Typography>

                  {/* Risk Rating Change (if applicable) */}
                  {hasRatingChange && (
                    <Box sx={{ bgcolor: 'action.hover', p: 1.5, borderRadius: 1, mb: 1 }}>
                      <Typography variant="body2" fontWeight="medium" gutterBottom>
                        Risk Rating Change
                      </Typography>
                      <Grid container spacing={2}>
                        {entry.previous_impact_rating && entry.new_impact_rating && (
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Impact Rating</Typography>
                            <Typography variant="body2">
                              {entry.previous_impact_rating} → {entry.new_impact_rating}
                            </Typography>
                          </Grid>
                        )}
                        {entry.previous_likelihood_rating && entry.new_likelihood_rating && (
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Likelihood Rating</Typography>
                            <Typography variant="body2">
                              {entry.previous_likelihood_rating} → {entry.new_likelihood_rating}
                            </Typography>
                          </Grid>
                        )}
                        {entry.previous_net_exposure && entry.new_net_exposure && (
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Net Exposure</Typography>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Chip
                                label={entry.previous_net_exposure}
                                color={entry.previous_net_exposure.includes('Critical') ? 'error' :
                                       entry.previous_net_exposure.includes('High') ? 'warning' :
                                       entry.previous_net_exposure.includes('Medium') ? 'info' : 'success'}
                                size="small"
                              />
                              <Typography variant="body2">→</Typography>
                              <Chip
                                label={entry.new_net_exposure}
                                color={entry.new_net_exposure.includes('Critical') ? 'error' :
                                       entry.new_net_exposure.includes('High') ? 'warning' :
                                       entry.new_net_exposure.includes('Medium') ? 'info' : 'success'}
                                size="small"
                              />
                            </Box>
                          </Grid>
                        )}
                      </Grid>
                    </Box>
                  )}

                  {/* Approval Status */}
                  {(entry.entry_status === 'Approved' || entry.entry_status === 'Rejected') && entry.reviewed_by && (
                    <Box display="flex" alignItems="center" gap={1} mt={1}>
                      <Typography variant="body2" color="text.secondary">
                        {entry.entry_status} by {entry.reviewed_by}
                      </Typography>
                      {entry.approved_date && (
                        <Typography variant="body2" color="text.secondary">
                          on {new Date(entry.approved_date).toLocaleDateString()}
                        </Typography>
                      )}
                    </Box>
                  )}

                  {/* Expandable Details */}
                  <Collapse in={isExpanded}>
                    <Divider sx={{ my: 2 }} />
                    <Grid container spacing={2}>
                      {entry.mitigation_actions_taken && (
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">
                            Mitigation Actions
                          </Typography>
                          <Typography variant="body2">
                            {entry.mitigation_actions_taken}
                          </Typography>
                        </Grid>
                      )}

                      {entry.business_justification && (
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">
                            Business Justification
                          </Typography>
                          <Typography variant="body2">
                            {entry.business_justification}
                          </Typography>
                        </Grid>
                      )}

                      {entry.supporting_evidence && (
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">
                            Supporting Evidence
                          </Typography>
                          <Typography variant="body2">
                            {entry.supporting_evidence}
                          </Typography>
                        </Grid>
                      )}

                      {entry.next_review_required && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Next Review Required
                          </Typography>
                          <Typography variant="body2">
                            {new Date(entry.next_review_required).toLocaleDateString()}
                          </Typography>
                        </Grid>
                      )}

                      {entry.risk_owner_at_time && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Risk Owner (at time of entry)
                          </Typography>
                          <Typography variant="body2">
                            {entry.risk_owner_at_time}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </Collapse>
                </CardContent>
              </Card>
            </Box>
          );
        })}
      </Box>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor?.element}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        {menuAnchor && (() => {
          const entry = logEntries.find(e => e.log_entry_id === menuAnchor.entryId);
          if (!entry) return null;

          const canEdit = entry.entry_status === 'Draft';
          const canApprove = entry.entry_status === 'Submitted' || entry.entry_status === 'Draft';

          return [
            canEdit && (
              <MenuItem key="edit" onClick={() => handleEdit(entry)}>
                <EditIcon sx={{ mr: 1 }} fontSize="small" />
                Edit
              </MenuItem>
            ),
            canApprove && entry.entry_status !== 'Approved' && (
              <MenuItem key="approve" onClick={() => handleApprovalAction(entry, 'approve')}>
                <ApproveIcon sx={{ mr: 1 }} fontSize="small" />
                Approve
              </MenuItem>
            ),
            canApprove && entry.entry_status !== 'Rejected' && (
              <MenuItem key="reject" onClick={() => handleApprovalAction(entry, 'reject')}>
                <RejectIcon sx={{ mr: 1 }} fontSize="small" />
                Reject
              </MenuItem>
            ),
            canEdit && (
              <MenuItem key="delete" onClick={() => handleDelete(entry.log_entry_id)} sx={{ color: 'error.main' }}>
                <DeleteIcon sx={{ mr: 1 }} fontSize="small" />
                Delete
              </MenuItem>
            ),
          ].filter(Boolean);
        })()}
      </Menu>

      {/* Approval/Rejection Dialog */}
      <Dialog
        open={approvalDialog.isOpen}
        onClose={() => setApprovalDialog({ isOpen: false, entry: null, action: 'approve' })}
      >
        <DialogTitle>
          {approvalDialog.action === 'approve' ? 'Approve' : 'Reject'} Log Entry
        </DialogTitle>
        <DialogContent>
          <Typography paragraph>
            Are you sure you want to {approvalDialog.action} this log entry?
          </Typography>
          {approvalDialog.action === 'approve' && approvalDialog.entry?.new_net_exposure && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Approving this entry will update the risk's net exposure to {approvalDialog.entry.new_net_exposure}.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setApprovalDialog({ isOpen: false, entry: null, action: 'approve' })}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            color={approvalDialog.action === 'approve' ? 'success' : 'error'}
            onClick={executeApprovalAction}
            disabled={isApproving || isRejecting}
          >
            {approvalDialog.action === 'approve' ? 'Approve' : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create/Edit Form Dialog */}
      <RiskLogEntryForm
        open={formDialog.isOpen}
        onClose={handleFormClose}
        risk={risk}
        logEntry={formDialog.editingEntry || undefined}
        currentUser={currentUser}
      />
    </Box>
  );
};
