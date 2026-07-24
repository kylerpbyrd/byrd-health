import { useQuery } from "@tanstack/react-query";
import { fetchCycles, fetchCycleDetail, fetchChartData } from "@/lib/api";
import type { Cycle, ChartData, CycleDetailComposed } from "@/types/fertility";

export function useCycles() {
  return useQuery<Cycle[]>({
    queryKey: ["cycles"],
    queryFn: fetchCycles,
  });
}

export function useCycleDetail(cycleId: string) {
  return useQuery<CycleDetailComposed>({
    queryKey: ["cycle", cycleId],
    queryFn: () => fetchCycleDetail(cycleId),
    enabled: !!cycleId,
  });
}

export function useChartData(cycleId: string) {
  return useQuery<ChartData>({
    queryKey: ["chart", cycleId],
    queryFn: () => fetchChartData(cycleId),
    enabled: !!cycleId,
  });
}
