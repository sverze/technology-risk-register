import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { riskLogEntryApi } from '@/services/api';
import type { RiskLogEntryUpdate } from '@/types/riskLogEntry';

export const useRiskLogEntries = (riskId: string) => {
  return useQuery({
    queryKey: ['risk-log-entries', riskId],
    queryFn: () => riskLogEntryApi.getLogEntries(riskId),
    enabled: !!riskId,
  });
};

export const useRiskLogEntry = (logEntryId: string) => {
  return useQuery({
    queryKey: ['risk-log-entry', logEntryId],
    queryFn: () => riskLogEntryApi.getLogEntry(logEntryId),
    enabled: !!logEntryId,
  });
};

export const useCreateRiskLogEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: riskLogEntryApi.createLogEntry,
    onSuccess: (newEntry) => {
      // Invalidate the log entries list for this risk
      queryClient.invalidateQueries({
        queryKey: ['risk-log-entries', newEntry.risk_id]
      });
      // Invalidate the individual risk data (in case it affects current ratings)
      queryClient.invalidateQueries({
        queryKey: ['risks', newEntry.risk_id]
      });
      // Invalidate dashboard data
      queryClient.invalidateQueries({
        queryKey: ['dashboard']
      });
    },
  });
};

export const useUpdateRiskLogEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logEntryId, updates }: { logEntryId: string; updates: RiskLogEntryUpdate }) =>
      riskLogEntryApi.updateLogEntry(logEntryId, updates),
    onSuccess: (updatedEntry) => {
      // Update the cache for this specific log entry
      queryClient.setQueryData(
        ['risk-log-entry', updatedEntry.log_entry_id],
        updatedEntry
      );
      // Invalidate the log entries list for this risk
      queryClient.invalidateQueries({
        queryKey: ['risk-log-entries', updatedEntry.risk_id]
      });
      // Invalidate the individual risk data
      queryClient.invalidateQueries({
        queryKey: ['risks', updatedEntry.risk_id]
      });
    },
  });
};

export const useApproveRiskLogEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logEntryId, reviewedBy }: { logEntryId: string; reviewedBy: string }) =>
      riskLogEntryApi.approveLogEntry(logEntryId, reviewedBy),
    onSuccess: (approvedEntry) => {
      // Update the cache for this specific log entry
      queryClient.setQueryData(
        ['risk-log-entry', approvedEntry.log_entry_id],
        approvedEntry
      );
      // Invalidate the log entries list for this risk
      queryClient.invalidateQueries({
        queryKey: ['risk-log-entries', approvedEntry.risk_id]
      });
      // Invalidate the individual risk data (rating may have changed)
      queryClient.invalidateQueries({
        queryKey: ['risks', approvedEntry.risk_id]
      });
      // Invalidate all risks list
      queryClient.invalidateQueries({
        queryKey: ['risks']
      });
      // Invalidate dashboard data
      queryClient.invalidateQueries({
        queryKey: ['dashboard']
      });
    },
  });
};

export const useRejectRiskLogEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logEntryId, reviewedBy }: { logEntryId: string; reviewedBy: string }) =>
      riskLogEntryApi.rejectLogEntry(logEntryId, reviewedBy),
    onSuccess: (rejectedEntry) => {
      // Update the cache for this specific log entry
      queryClient.setQueryData(
        ['risk-log-entry', rejectedEntry.log_entry_id],
        rejectedEntry
      );
      // Invalidate the log entries list for this risk
      queryClient.invalidateQueries({
        queryKey: ['risk-log-entries', rejectedEntry.risk_id]
      });
    },
  });
};

export const useDeleteRiskLogEntry = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: riskLogEntryApi.deleteLogEntry,
    onSuccess: (_, logEntryId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: ['risk-log-entry', logEntryId] });
      // Invalidate all risk log entries queries
      queryClient.invalidateQueries({ queryKey: ['risk-log-entries'] });
      // Invalidate risks
      queryClient.invalidateQueries({ queryKey: ['risks'] });
    },
  });
};
