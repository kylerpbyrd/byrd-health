import { useQuery } from "@tanstack/react-query";
import { fetchCalendar } from "@/lib/api";
import type { CalendarResponse } from "@/types/fertility";

export function useCalendar(month: string) {
  return useQuery<CalendarResponse>({
    queryKey: ["calendar", month],
    queryFn: () => fetchCalendar(month),
  });
}
