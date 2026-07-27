import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchPregnancy, startPregnancy, updatePregnancy } from "@/lib/api";
import type { PregnancyResponse } from "@/types/fertility";

export function usePregnancy() {
  return useQuery<PregnancyResponse | null>({
    queryKey: ["pregnancy"],
    queryFn: async () => {
      try {
        return await fetchPregnancy();
      } catch {
        return null;
      }
    },
    retry: false,
  });
}

export function useStartPregnancy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: startPregnancy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pregnancy"] });
    },
  });
}

export function useUpdatePregnancy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updatePregnancy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pregnancy"] });
    },
  });
}
