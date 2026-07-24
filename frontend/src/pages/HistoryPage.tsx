import { useNavigate } from "react-router-dom";
import { useCycles } from "@/hooks/useCycles";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { Loader2 } from "lucide-react";

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
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          )}

          {isError && (
            <p className="py-8 text-center text-muted-foreground">
              Unable to load cycle history.
            </p>
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
