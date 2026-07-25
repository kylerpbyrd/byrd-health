import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchDashboard, reanalyzeInsights, fetchChartData, fetchTodayEntry } from "@/lib/api";
import type { DashboardData, InsightsResponse, ChartData, EntryResponse } from "@/types/fertility";

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

export function useChartData() {
  const { data: dashboard } = useDashboard();
  const cycleId = dashboard?.cycleId;

  return useQuery<ChartData>({
    queryKey: ["chart", cycleId],
    queryFn: () => fetchChartData(cycleId!),
    enabled: !!cycleId,
  });
}

export function useTodayEntry() {
  return useQuery<EntryResponse | null>({
    queryKey: ["todayEntry"],
    queryFn: fetchTodayEntry,
  });
}
