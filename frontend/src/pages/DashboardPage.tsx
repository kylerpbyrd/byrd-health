import { useDashboard, useChartData, useTodayEntry } from "@/hooks/useDashboard";
import { PhaseBanner } from "@/components/PhaseBanner";
import { StatTile } from "@/components/StatTile";
import { WarningBanner } from "@/components/WarningBanner";
import { BBTChart } from "@/components/BBTChart";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { formatShortDate } from "@/lib/utils";
import { Loader2 } from "lucide-react";
import type { ChartData } from "@/types/fertility";

function formatWindow(start: string | null, end: string | null): string {
  if (!start || !end) return "—";
  return `${formatShortDate(start)} – ${formatShortDate(end)}`;
}

function formatSignValue(val: string): string {
  if (!val) return "Not logged";
  return val.charAt(0).toUpperCase() + val.slice(1).replace(/_/g, " ");
}

const EMPTY_CHART: ChartData = {
  labels: [],
  temperatures: [],
  discarded: [],
  coverline: null,
  fertile_start_day: null,
  fertile_end_day: null,
  ovulation_day: null,
  mucus: {},
  opk: {},
  unit: "F",
};

export default function DashboardPage() {
  const { data, isLoading, isError } = useDashboard();
  const { data: chartData } = useChartData();
  const { data: todayEntry } = useTodayEntry();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="py-20 text-center text-muted-foreground">
        Unable to load dashboard data.
      </div>
    );
  }

  const ovulationStatus = data.ovulation_date
    ? `${formatShortDate(data.ovulation_date)}${data.ovulation_confirmed ? " ✓" : " ?"}`
    : "—";

  return (
    <div>
      <PhaseBanner
        phase={data.phase}
        cycleDay={data.cycle_day}
        avgCycleLength={data.avg_cycle_length}
      />

      {data.last_temp && (
        <div className="mb-4 text-center">
          <span className="inline-flex items-center gap-1 rounded-full bg-accent px-4 py-1.5 text-sm font-medium text-accent-foreground">
            Last Temp: {data.last_temp.toFixed(2)}°F
          </span>
        </div>
      )}

      {data.warnings.map((w, i) => (
        <WarningBanner key={i} type={w.type as "warning" | "info"} message={w.message} />
      ))}

      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile value={data.cycle_day} label="Cycle Day" />
        <StatTile
          value={data.next_period_date ? formatShortDate(data.next_period_date) : "—"}
          label="Next Period Est."
        />
        <StatTile
          value={formatWindow(data.fertile_start_date, data.fertile_end_date)}
          label="Fertile Window"
        />
        <StatTile value={ovulationStatus} label="Ovulation" />
      </div>

      <Card className="mb-6">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-base">BBT Chart</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/history")}
            className="text-xs"
          >
            Full chart →
          </Button>
        </CardHeader>
        <CardContent>
          <BBTChart chartData={chartData || EMPTY_CHART} height={220} mini />
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Today&apos;s Signs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">Mucus: {formatSignValue(todayEntry?.signs?.cervical_mucus ?? "")}</Badge>
            <Badge variant="secondary">OPK: {formatSignValue(todayEntry?.signs?.opk_result ?? "")}</Badge>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Button size="lg" onClick={() => navigate("/entry")}>
          Log Today&apos;s Entry
        </Button>
        <Button variant="outline" size="lg" onClick={() => navigate("/history")}>
          View Cycle History
        </Button>
      </div>
    </div>
  );
}
