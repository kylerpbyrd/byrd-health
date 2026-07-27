import { useQuery } from "@tanstack/react-query";
import { fetchSymptomCatalog } from "@/lib/api";

export function useSymptomCatalog(category?: string) {
  return useQuery({
    queryKey: ["symptomCatalog", category],
    queryFn: () => fetchSymptomCatalog(category),
  });
}
