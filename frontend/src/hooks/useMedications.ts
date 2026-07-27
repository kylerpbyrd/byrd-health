import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchMedications, createMedication } from "@/lib/api";
import type { MedicationLog, CreateMedicationPayload } from "@/lib/api";

export function useMedications() {
  return useQuery<MedicationLog[]>({
    queryKey: ["medications"],
    queryFn: fetchMedications,
  });
}

export function useCreateMedication() {
  const queryClient = useQueryClient();
  return useMutation<MedicationLog, Error, CreateMedicationPayload>({
    mutationFn: createMedication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["medications"] });
    },
  });
}
