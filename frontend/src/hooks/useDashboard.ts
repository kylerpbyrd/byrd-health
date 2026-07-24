import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchDashboard, reanalyzeInsights } from "@/lib/api";
import type { DashboardData, InsightsResponse } from "@/types/fertility";

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
  });
}

export function useReanalyzeInsights() {
  const queryClient = useQueryClient();
  return useMutation<InsightsResponse, Error>({
    mutationFn: reanalyzeInsights,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
