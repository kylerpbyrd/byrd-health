import { useNavigate } from "react-router-dom";
import { useCycles } from "@/hooks/useCycles";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/Skeleton";
import { formatDate } from "@/lib/utils";
import { CalendarDays } from "lucide-react";

export default function HistoryPage() {
  const { data: cycles, isLoading, isError } = useCycles();
  const navigate = useNavigate();

  return (
    <div>
      <button
        onClick={() => navigate("/")}
        className="mb-4 text-sm text-muted-foreground hover:text-foreground"
      >
        ← Dashboard
      </button>

      <Card>
        <CardHeader>
          <CardTitle>Cycle History</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-3 py-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="rounded-lg border p-4">
                  <Skeleton className="h-5 w-32 mb-2" />
                  <Skeleton className="h-4 w-48" />
                </div>
              ))}
            </div>
          )}

          {isError && (
            <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
              <CalendarDays className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground max-w-md">
                No cycles found. Start logging entries to track your fertility patterns over time.
              </p>
            </div>
          )}

          {!isLoading && !isError && cycles && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Cycle</th>
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Start Date</th>
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Length</th>
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Ovulation</th>
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Luteal</th>
                    <th className="pb-3 pr-4 font-medium text-muted-foreground">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {cycles.map((cycle, idx) => (
                    <tr
                      key={cycle.id}
                      className="cursor-pointer border-b transition-colors hover:bg-accent/50"
                      onClick={() => navigate(`/history/${cycle.id}`)}
                    >
                      <td className="py-3 pr-4 font-medium">
                        #{cycles.length - idx}
                      </td>
                      <td className="py-3 pr-4">{formatDate(cycle.start_date)}</td>
                      <td className="py-3 pr-4">
                        {cycle.cycle_length ? `${cycle.cycle_length} days` : "—"}
                      </td>
                      <td className="py-3 pr-4">
                        {cycle.ovulation_date
                          ? `${formatDate(cycle.ovulation_date)}${cycle.ovulation_confirmed ? " ✓" : ""}`
                          : "—"}
                      </td>
                      <td className="py-3 pr-4">
                        {cycle.luteal_length ? `${cycle.luteal_length} days` : "—"}
                      </td>
                      <td className="py-3 pr-4">
                        <Badge variant={cycle.is_active ? "default" : "secondary"}>
                          {cycle.is_active ? "Active" : "Complete"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
