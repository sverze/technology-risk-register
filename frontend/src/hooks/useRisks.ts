import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { riskApi } from '@/services/api';
import type { Risk } from '@/types/risk';

export const useRisks = (params?: Parameters<typeof riskApi.getRisks>[0]) => {
  return useQuery({
    queryKey: ['risks', params],
    queryFn: () => riskApi.getRisks(params),
  });
};

export const useRisk = (riskId: string) => {
  return useQuery({
    queryKey: ['risks', riskId],
    queryFn: () => riskApi.getRisk(riskId),
    enabled: !!riskId,
  });
};

export const useCreateRisk = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: riskApi.createRisk,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateRisk = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ riskId, data }: { riskId: string; data: Partial<Risk> }) =>
      riskApi.updateRisk(riskId, data),
    onSuccess: (_, { riskId }) => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
      queryClient.invalidateQueries({ queryKey: ['risks', riskId] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['risk-updates', riskId] });
    },
  });
};

export const useDeleteRisk = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: riskApi.deleteRisk,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useRiskUpdates = (riskId: string) => {
  return useQuery({
    queryKey: ['risk-updates', riskId],
    queryFn: () => riskApi.getRiskUpdates(riskId),
    enabled: !!riskId,
  });
};

export const useRecentUpdates = (limit?: number) => {
  return useQuery({
    queryKey: ['recent-updates', limit],
    queryFn: () => riskApi.getRecentUpdates(limit),
  });
};
