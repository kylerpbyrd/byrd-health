import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/Skeleton";
import { usePregnancy, useStartPregnancy, useUpdatePregnancy } from "@/hooks/usePregnancy";
import { useCycles } from "@/hooks/useCycles";
import { formatDate } from "@/lib/utils";
import { Baby, Calendar } from "lucide-react";

const TRIMESTER_INFO: Record<number, { title: string; milestones: string[] }> = {
  1: {
    title: "First Trimester",
    milestones: [
      "Baby's neural tube, brain, and spinal cord begin to form",
      "Heart begins to beat around week 6",
      "All major organs have formed by week 12",
      "Morning sickness, fatigue, and breast tenderness are common",
    ],
  },
  2: {
    title: "Second Trimester",
    milestones: [
      "Baby begins to move, kick, and swallow",
      "Hair, eyebrows, and eyelashes appear",
      "Baby can hear your voice by week 18",
      "Nausea often subsides and energy returns",
    ],
  },
  3: {
    title: "Third Trimester",
    milestones: [
      "Baby gains significant weight and body fat",
      "Lungs mature and brain develops rapidly",
      "Braxton Hicks contractions may begin",
      "Baby typically positions head-down for birth",
    ],
  },
};

function formatCountdown(dateStr: string): string {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(dateStr + "T00:00:00");
  const diff = Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  if (diff < 0) return `${Math.abs(diff)} days past due`;
  if (diff === 0) return "Due today";
  return `${diff} days remaining`;
}

function SkeletonLoader() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-[120px] w-full rounded-lg" />
      <Skeleton className="h-[200px] w-full rounded-lg" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Skeleton className="h-24 rounded-lg" />
        <Skeleton className="h-24 rounded-lg" />
      </div>
    </div>
  );
}

export default function PregnancyPage() {
  const navigate = useNavigate();
  const { data: pregnancy, isLoading, isError, refetch } = usePregnancy();
  const { data: cycles = [] } = useCycles();
  const startMutation = useStartPregnancy();
  const updateMutation = useUpdatePregnancy();

  const [showForm, setShowForm] = useState(false);
  const [selectedCycleId, setSelectedCycleId] = useState("");
  const [lmpDate, setLmpDate] = useState("");
  const [ovulationDate, setOvulationDate] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (pregnancy) {
      setNotes(pregnancy.notes ?? "");
    }
  }, [pregnancy]);

  const handleStartTracking = () => {
    if (!selectedCycleId || !lmpDate) {
      toast.error("Please select a cycle and enter your LMP date.");
      return;
    }
    startMutation.mutate(
      {
        cycle_id: selectedCycleId,
        lmp_date: lmpDate,
        ...(ovulationDate ? { ovulation_date: ovulationDate } : {}),
      },
      {
        onSuccess: () => {
          setShowForm(false);
          toast.success("Pregnancy tracking started!");
        },
        onError: (err) => {
          toast.error(err.message || "Failed to start pregnancy tracking");
        },
      }
    );
  };

  const handleToggleForm = () => {
    setShowForm(!showForm);
  };

  const handleSaveNotes = () => {
    updateMutation.mutate(
      { notes },
      {
        onSuccess: () => {
          toast.success("Notes saved");
        },
        onError: (err) => {
          toast.error(err.message || "Failed to save notes");
        },
      }
    );
  };

  const handleEndTracking = () => {
    if (!window.confirm("Are you sure you want to end pregnancy tracking? This cannot be undone.")) {
      return;
    }
    updateMutation.mutate(
      { is_active: false },
      {
        onSuccess: () => {
          setNotes("");
          toast.success("Pregnancy tracking ended");
        },
        onError: (err) => {
          toast.error(err.message || "Failed to end tracking");
        },
      }
    );
  };

  if (isLoading) return <SkeletonLoader />;

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
        <Baby className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground mb-4">Failed to load pregnancy data</p>
        <Button onClick={() => refetch()}>Retry</Button>
      </div>
    );
  }

  const hasPregnancy = pregnancy && pregnancy.is_active;

  return (
    <div>
      <button
        onClick={() => navigate("/")}
        className="mb-4 text-sm text-muted-foreground hover:text-foreground"
      >
        ← Dashboard
      </button>

      {!hasPregnancy && !showForm && (
        <Card className="text-center">
          <CardContent className="pt-6 pb-6">
            <Baby className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Pregnancy Tracking</h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Track your pregnancy journey. Get your due date, weekly milestones, and developmental updates.
            </p>
            <Button onClick={handleToggleForm} size="lg">
              Start Tracking
            </Button>
          </CardContent>
        </Card>
      )}

      {!hasPregnancy && showForm && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Start Pregnancy Tracking</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Cycle</label>
              <Select
                options={[
                  { value: "", label: "Select a cycle..." },
                  ...cycles.map((c) => ({
                    value: c.id,
                    label: `${formatDate(c.start_date)}${c.end_date ? ` — ${formatDate(c.end_date)}` : " (active)"}`,
                  })),
                ]}
                value={selectedCycleId}
                onChange={(e) => setSelectedCycleId(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Last Menstrual Period (LMP) Date</label>
              <input
                type="date"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={lmpDate}
                onChange={(e) => setLmpDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Ovulation Date <span className="text-muted-foreground font-normal">(optional)</span>
              </label>
              <input
                type="date"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={ovulationDate}
                onChange={(e) => setOvulationDate(e.target.value)}
              />
            </div>

            <div className="flex gap-2 pt-2">
              <Button onClick={handleStartTracking} disabled={startMutation.isPending}>
                {startMutation.isPending ? "Starting..." : "Start Tracking"}
              </Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {hasPregnancy && pregnancy && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Your Pregnancy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Due Date</p>
                <p className="text-2xl font-bold">
                  {pregnancy.due_date ? formatDate(pregnancy.due_date) : "Calculating..."}
                </p>
                {pregnancy.days_remaining !== null && (
                  <p className="text-sm text-muted-foreground mt-1">
                    {formatCountdown(pregnancy.due_date!)}
                  </p>
                )}
              </div>

              {pregnancy.current_week !== null && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Week {pregnancy.current_week}</span>
                    <span className="text-muted-foreground">Week 40</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{
                        width: `${Math.min(Math.round((pregnancy.current_week / 40) * 100), 100)}%`,
                      }}
                    />
                  </div>
                </div>
              )}

              {pregnancy.trimester !== null && (
                <div className="flex justify-center">
                  <Badge className="text-sm px-4 py-1">
                    {TRIMESTER_INFO[pregnancy.trimester]?.title ?? `Trimester ${pregnancy.trimester}`}
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>

          {pregnancy.trimester !== null && TRIMESTER_INFO[pregnancy.trimester] && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  {TRIMESTER_INFO[pregnancy.trimester].title} Milestones
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {TRIMESTER_INFO[pregnancy.trimester].milestones.map((m, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="text-primary mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full bg-primary" />
                      {m}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Notes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <textarea
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Add your thoughts, symptoms, questions for your provider..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
              <div className="flex gap-2">
                <Button onClick={handleSaveNotes} disabled={updateMutation.isPending} size="sm">
                  {updateMutation.isPending ? "Saving..." : "Save Notes"}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="border-destructive/30">
            <CardContent className="pt-6 pb-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">End Pregnancy Tracking</p>
                  <p className="text-sm text-muted-foreground">
                    This will mark the pregnancy as no longer active.
                  </p>
                </div>
                <Button variant="destructive" onClick={handleEndTracking} size="sm">
                  End Tracking
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
