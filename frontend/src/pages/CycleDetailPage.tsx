import { useParams, useNavigate } from "react-router-dom";
import { useCycleDetail, useChartData } from "@/hooks/useCycles";
import { BBTChart } from "@/components/BBTChart";
import { StatTile } from "@/components/StatTile";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { Loader2 } from "lucide-react";

export default function CycleDetailPage() {
  const { cycleId } = useParams<{ cycleId: string }>();
  const navigate = useNavigate();
  const { data: detail, isLoading: detailLoading } = useCycleDetail(cycleId!);
  const { data: chartData, isLoading: chartLoading } = useChartData(cycleId!);

  const isLoading = detailLoading || chartLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!detail || !chartData) {
    return (
      <div className="py-20 text-center text-muted-foreground">
        Cycle not found.
      </div>
    );
  }

  const { cycle, insights, entries } = detail;

  return (
    <div>
      <button
        onClick={() => navigate("/history")}
        className="mb-4 text-sm text-muted-foreground hover:text-foreground"
      >
        ← History
      </button>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Cycle Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            <StatTile
              value={cycle.cycle_length ? `${cycle.cycle_length} days` : "—"}
              label="Length"
            />
            <StatTile
              value={cycle.start_date ? formatDate(cycle.start_date) : "—"}
              label="Start"
              subtext={cycle.end_date ? `to ${formatDate(cycle.end_date)}` : undefined}
            />
            <StatTile
              value={
                insights.ovulation_date
                  ? `${formatDate(insights.ovulation_date)}${insights.ovulation_confirmed ? " ✓" : ""}`
                  : "—"
              }
              label="Ovulation"
            />
            <StatTile
              value={insights.luteal_length ? `${insights.luteal_length} days` : "—"}
              label="Luteal Phase"
              subtext={insights.luteal_phase_short ? "Short" : undefined}
            />
            <StatTile
              value={insights.coverline ? `${insights.coverline.toFixed(2)}°F` : "—"}
              label="Coverline"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>BBT Chart</CardTitle>
        </CardHeader>
        <CardContent>
          <BBTChart chartData={chartData} height={350} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Daily Log</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="pb-3 pr-4 font-medium text-muted-foreground">Day</th>
                  <th className="pb-3 pr-4 font-medium text-muted-foreground">Date</th>
                  <th className="pb-3 pr-4 font-medium text-muted-foreground">Temp</th>
                  <th className="pb-3 pr-4 font-medium text-muted-foreground">Flow</th>
                  <th className="pb-3 pr-4 font-medium text-muted-foreground">Mucus</th>
                  <th className="pb-3 pr-4 font-medium text-muted-foreground">OPK</th>
                  <th className="pb-3 pr-4 font-medium text-muted-foreground">Symptoms</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry, i) => (
                  <tr key={i} className="border-b">
                    <td className="py-2 pr-4 font-medium">{entry.day as number}</td>
                    <td className="py-2 pr-4">{formatDate(entry.date as string)}</td>
                    <td className="py-2 pr-4">
                      {entry.temp != null ? `${(entry.temp as number).toFixed(2)}°F` : "—"}
                    </td>
                    <td className="py-2 pr-4 capitalize">
                      {(entry.flow as string) || "—"}
                    </td>
                    <td className="py-2 pr-4 capitalize">
                      {(entry.mucus as string)?.replace("_", " ") || "—"}
                    </td>
                    <td className="py-2 pr-4 capitalize">
                      {(entry.opk as string)?.replace("_", " ") || "—"}
                    </td>
                    <td className="py-2 pr-4">
                      <div className="flex flex-wrap gap-1">
                        {(entry.symptoms as string[])?.length > 0
                          ? (entry.symptoms as string[]).map((s) => (
                              <Badge key={s} variant="outline" className="text-xs">
                                {s.replace("_", " ")}
                              </Badge>
                            ))
                          : "—"}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
