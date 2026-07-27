import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useMedications, useCreateMedication } from "@/hooks/useMedications";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/Skeleton";
import { formatDate } from "@/lib/utils";
import { Pill } from "lucide-react";

const SCHEDULE_OPTIONS = [
  { value: "daily", label: "Daily" },
  { value: "as_needed", label: "As Needed" },
  { value: "weekly", label: "Weekly" },
];

export default function MedicationsPage() {
  const navigate = useNavigate();
  const { data: medications, isLoading, isError } = useMedications();
  const createMutation = useCreateMedication();

  const [name, setName] = useState("");
  const [dosage, setDosage] = useState("");
  const [schedule, setSchedule] = useState("daily");
  const [notes, setNotes] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error("Medication name is required");
      return;
    }
    try {
      await createMutation.mutateAsync({
        name: name.trim(),
        dosage: dosage.trim() || undefined,
        schedule,
        notes: notes.trim() || undefined,
      });
      toast.success("Medication logged");
      setName("");
      setDosage("");
      setSchedule("daily");
      setNotes("");
    } catch {
      toast.error("Failed to log medication");
    }
  };

  return (
    <div>
      <button
        onClick={() => navigate("/")}
        className="mb-4 text-sm text-muted-foreground hover:text-foreground"
      >
        ← Dashboard
      </button>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Log Medication</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="med-name">Medication Name</Label>
              <Input
                id="med-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Ibuprofen"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="med-dosage">Dosage (optional)</Label>
              <Input
                id="med-dosage"
                value={dosage}
                onChange={(e) => setDosage(e.target.value)}
                placeholder="e.g. 400mg"
              />
            </div>
            <div className="space-y-2">
              <Label>Schedule</Label>
              <div className="flex flex-wrap gap-2">
                {SCHEDULE_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className={`inline-flex cursor-pointer items-center rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                      schedule === opt.value
                        ? "border-primary bg-accent text-accent-foreground"
                        : "border-input bg-background text-muted-foreground hover:bg-accent/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="schedule"
                      value={opt.value}
                      checked={schedule === opt.value}
                      onChange={(e) => setSchedule(e.target.value)}
                      className="sr-only"
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="med-notes">Notes (optional)</Label>
              <textarea
                id="med-notes"
                rows={2}
                placeholder="Any additional notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            <Button type="submit" className="w-full" disabled={createMutation.isPending}>
              {createMutation.isPending ? "Saving..." : "Log Medication"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Pill className="h-5 w-5" />
            Recent Medications
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-3 py-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="rounded-lg border p-4">
                  <Skeleton className="h-5 w-32 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </div>
              ))}
            </div>
          )}
          {isError && (
            <p className="py-8 text-center text-muted-foreground">
              Failed to load medications
            </p>
          )}
          {!isLoading && !isError && medications?.length === 0 && (
            <p className="py-8 text-center text-muted-foreground">
              No medications logged yet
            </p>
          )}
          {!isLoading && !isError && medications && medications.length > 0 && (
            <div className="space-y-3">
              {medications.map((med) => (
                <div
                  key={med.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div>
                    <p className="font-medium">{med.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {med.dosage && `${med.dosage} — `}
                      <Badge variant="secondary" className="ml-1">
                        {med.schedule.replace("_", " ")}
                      </Badge>
                    </p>
                    {med.notes && (
                      <p className="mt-1 text-xs text-muted-foreground">{med.notes}</p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(med.created_at)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
