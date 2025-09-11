import { useQuery } from '@tanstack/react-query';
import { dropdownApi } from '@/services/api';

export const useDropdownValues = () => {
  return useQuery({
    queryKey: ['dropdown-values'],
    queryFn: dropdownApi.getDropdownValues,
    staleTime: 30 * 60 * 1000, // 30 minutes - dropdown values change rarely
    gcTime: 60 * 60 * 1000, // 1 hour
  });
};
