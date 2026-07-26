import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useCalendar } from "@/hooks/useCalendar";
import { createEntry } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/Skeleton";
import { cn, formatTemp } from "@/lib/utils";
import {
  ChevronLeft,
  ChevronRight,
  CalendarDays,
  Droplet,
  Beaker,
  Waves,
  Egg,
  X,
} from "lucide-react";
import type { CalendarDay } from "@/types/fertility";

function monthKey(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  return `${y}-${m}`;
}

function todayKey(): string {
  return monthKey(new Date());
}

function monthLabel(key: string): string {
  const [y, m] = key.split("-").map(Number);
  return new Date(y, m - 1).toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });
}

function addMonths(key: string, delta: number): string {
  const [y, m] = key.split("-").map(Number);
  const d = new Date(y, m - 1 + delta, 1);
  return monthKey(d);
}

const DAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];

const phaseBg: Record<string, string> = {
  menstruation: "bg-red-50",
  follicular: "bg-emerald-50",
  fertile: "bg-purple-50",
  luteal: "bg-blue-50",
};

const phaseBorder: Record<string, string> = {
  menstruation: "border-red-200",
  follicular: "border-emerald-200",
  fertile: "border-purple-200",
  luteal: "border-blue-200",
};

const FLOW_OPTIONS = [
  { value: "", label: "None" },
  { value: "spotting", label: "Spotting" },
  { value: "light", label: "Light" },
  { value: "medium", label: "Medium" },
  { value: "heavy", label: "Heavy" },
];

const MUCUS_OPTIONS = [
  { value: "", label: "None" },
  { value: "dry", label: "Dry" },
  { value: "sticky", label: "Sticky" },
  { value: "creamy", label: "Creamy" },
  { value: "watery", label: "Watery" },
  { value: "egg_white", label: "Egg White" },
];

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-7 gap-px bg-muted rounded-lg overflow-hidden">
      {Array.from({ length: 42 }).map((_, i) => (
        <div key={i} className="aspect-square bg-white p-1">
          <Skeleton className="h-4 w-5 mb-1" />
          <Skeleton className="h-3 w-8" />
        </div>
      ))}
    </div>
  );
}

function QuickEntryModal({
  dateStr,
  tempUnit,
  onClose,
}: {
  dateStr: string;
  tempUnit: string;
  onClose: () => void;
}) {
  const [tempVal, setTempVal] = useState("");
  const [flow, setFlow] = useState("");
  const [mucus, setMucus] = useState("");
  const [opk, setOpk] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const queryClient = useQueryClient();

  const formatted = new Date(dateStr + "T00:00:00").toLocaleDateString(
    "en-US",
    { weekday: "short", month: "short", day: "numeric" }
  );

  async function handleSave() {
    setSaving(true);
    setError("");
    try {
      await createEntry({
        date: dateStr,
        temp_value: tempVal,
        time_taken: "",
        is_discarded: false,
        discard_reason: "",
        menstrual_flow: flow,
        cervical_mucus: mucus,
        cervical_position: "",
        cervical_firmness: "",
        cervical_opening: "",
        opk_result: opk,
        symptoms: [],
        symptom_severity: 1,
        is_period_start: false,
        notes: "",
      });
      queryClient.invalidateQueries({ queryKey: ["calendar"] });
      onClose();
    } catch {
      setError("Failed to save entry");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl w-full max-w-sm mx-4 p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-lg">{formatted}</h3>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {error && (
          <p className="text-red-500 text-sm mb-3">{error}</p>
        )}

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">
              Temperature (&#176;{tempUnit})
            </label>
            <input
              type="number"
              step="0.01"
              value={tempVal}
              onChange={(e) => setTempVal(e.target.value)}
              placeholder="97.80"
              className="w-full rounded-md border px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Flow</label>
            <select
              value={flow}
              onChange={(e) => setFlow(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
            >
              {FLOW_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Mucus</label>
            <select
              value={mucus}
              onChange={(e) => setMucus(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
            >
              {MUCUS_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">OPK</label>
            <select
              value={opk}
              onChange={(e) => setOpk(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm"
            >
              <option value="">None</option>
              <option value="negative">Negative</option>
              <option value="positive">Positive</option>
              <option value="peak">Peak</option>
            </select>
          </div>
        </div>

        <div className="flex gap-2 mt-5">
          <Button onClick={handleSave} disabled={saving} className="flex-1">
            {saving ? "Saving..." : "Save"}
          </Button>
          <Button variant="outline" onClick={onClose} className="flex-1">
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function CalendarPage() {
  const [month, setMonth] = useState(todayKey());
  const { data, isLoading, isError } = useCalendar(month);
  const [modalDate, setModalDate] = useState<string | null>(null);
  const navigate = useNavigate();

  const goNow = () => setMonth(todayKey());

  const days = useMemo(() => {
    if (!data) return [];
    return data.days;
  }, [data]);

  const tempUnit = data?.profile.temp_unit || "F";

  function navigateToDay(dateStr: string) {
    if (!data?.cycles_in_range?.length) {
      setModalDate(dateStr);
      return;
    }
    for (const c of data.cycles_in_range) {
      if (!c.phase_dates) continue;
      for (const dates of Object.values(c.phase_dates)) {
        if (dates.includes(dateStr)) {
          setModalDate(dateStr);
          return;
        }
      }
    }
    setModalDate(dateStr);
  }

  if (isLoading) {
    return (
      <div>
        <div className="flex items-center justify-between mb-4">
          <Skeleton className="h-8 w-40" />
          <div className="flex gap-2">
            <Skeleton className="h-9 w-9 rounded-md" />
            <Skeleton className="h-9 w-20 rounded-md" />
            <Skeleton className="h-9 w-9 rounded-md" />
          </div>
        </div>
        <div className="grid grid-cols-7 mb-1">
          {DAY_LABELS.map((l) => (
            <div
              key={l}
              className="text-center text-xs font-medium text-muted-foreground py-2"
            >
              {l}
            </div>
          ))}
        </div>
        <SkeletonGrid />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
        <CalendarDays className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground max-w-md">
          Start tracking to see your calendar
        </p>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => navigate("/entry")}
        >
          Log Entry
        </Button>
      </div>
    );
  }

  const rows = [];
  for (let i = 0; i < days.length; i += 7) {
    rows.push(days.slice(i, i + 7));
  }

  return (
    <div>
      {modalDate && (
        <QuickEntryModal
          dateStr={modalDate}
          tempUnit={tempUnit}
          onClose={() => setModalDate(null)}
        />
      )}

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">{monthLabel(month)}</h2>
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setMonth(addMonths(month, -1))}
            aria-label="Previous month"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={goNow}>
            Today
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setMonth(addMonths(month, 1))}
            aria-label="Next month"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-7 mb-1">
        {DAY_LABELS.map((l) => (
          <div
            key={l}
            className="text-center text-xs font-medium text-muted-foreground py-2"
          >
            {l}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-px bg-muted rounded-lg overflow-hidden">
        {days.map((day) => (
          <CalendarCell
            key={day.date}
            day={day}
            tempUnit={tempUnit}
            onClick={() => navigateToDay(day.date)}
          />
        ))}
      </div>

      <div className="flex gap-4 mt-4 flex-wrap text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded-sm bg-red-50 border border-red-200" />
          Menstruation
        </span>
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded-sm bg-emerald-50 border border-emerald-200" />
          Follicular
        </span>
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded-sm bg-purple-50 border border-purple-200" />
          Fertile
        </span>
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded-sm bg-blue-50 border border-blue-200" />
          Luteal
        </span>
      </div>
    </div>
  );
}

function CalendarCell({
  day,
  tempUnit,
  onClick,
}: {
  day: CalendarDay;
  tempUnit: string;
  onClick: () => void;
}) {
  const dayNum = new Date(day.date + "T00:00:00").getDate();

  const bg = day.phase ? phaseBg[day.phase] || "bg-white" : "bg-white";
  const border = day.phase
    ? phaseBorder[day.phase] || "border-transparent"
    : "border-transparent";

  return (
    <button
      onClick={onClick}
      className={cn(
        "aspect-square p-1 text-left transition-colors hover:bg-accent/30 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-inset",
        bg,
        day.is_today && "ring-2 ring-primary ring-inset",
        day.in_current_month ? "border" : "opacity-50",
        !day.in_current_month && "border border-transparent"
      )}
      aria-label={`${day.date}${day.phase ? `, ${day.phase}` : ""}${day.has_entry ? ", has entry" : ""}`}
    >
      <div className="flex flex-col h-full min-h-[44px]">
        <div className="flex items-center justify-between">
          <span
            className={cn(
              "text-xs font-medium tabular-nums",
              !day.in_current_month && "text-muted-foreground/50",
              day.in_current_month && "text-foreground"
            )}
          >
            {dayNum}
          </span>
          <div className="flex gap-0.5">
            {day.is_ovulation_day && (
              <Egg className="h-3 w-3 text-amber-500" aria-label="Ovulation day" />
            )}
          </div>
        </div>

        {day.temp !== null && (
          <span className="text-[10px] text-muted-foreground mt-0.5 leading-tight">
            {formatTemp(day.temp, tempUnit as "F" | "C")}
          </span>
        )}

        {day.cycle_day !== null && (
          <span className="text-[10px] text-muted-foreground/70 mt-auto">
            CD {day.cycle_day}
          </span>
        )}

        <div className="flex gap-0.5 mt-auto">
          {day.flow && (
            <Droplet
              className="h-3 w-3 text-red-400"
              aria-label={`Flow: ${day.flow}`}
            />
          )}
          {day.mucus && (
            <Waves
              className="h-3 w-3 text-cyan-400"
              aria-label={`Mucus: ${day.mucus}`}
            />
          )}
          {day.opk && (
            <Beaker
              className="h-3 w-3 text-amber-500"
              aria-label={`OPK: ${day.opk}`}
            />
          )}
        </div>
      </div>
    </button>
  );
}
