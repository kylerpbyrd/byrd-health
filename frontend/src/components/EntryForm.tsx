import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { EntryFormData } from "@/types/fertility";

const TODAY = new Date().toISOString().slice(0, 10);

const FLOW_OPTIONS = [
  { value: "", label: "Not logged" },
  { value: "none", label: "None" },
  { value: "spotting", label: "Spotting" },
  { value: "light", label: "Light" },
  { value: "medium", label: "Medium" },
  { value: "heavy", label: "Heavy" },
];

const MUCUS_OPTIONS = [
  { value: "", label: "Not logged" },
  { value: "dry", label: "Dry" },
  { value: "sticky", label: "Sticky" },
  { value: "creamy", label: "Creamy" },
  { value: "watery", label: "Watery" },
  { value: "egg_white", label: "Egg White" },
];

const OPK_OPTIONS = [
  { value: "not_tested", label: "Not Tested" },
  { value: "negative", label: "Negative" },
  { value: "low", label: "Low" },
  { value: "high", label: "High" },
  { value: "peak", label: "Peak / Positive" },
];

const POSITION_OPTIONS = [
  { value: "", label: "Not checked" },
  { value: "low", label: "Low" },
  { value: "mid", label: "Mid" },
  { value: "high", label: "High" },
];

const FIRMNESS_OPTIONS = [
  { value: "", label: "—" },
  { value: "firm", label: "Firm" },
  { value: "medium", label: "Medium" },
  { value: "soft", label: "Soft" },
];

const OPENING_OPTIONS = [
  { value: "", label: "—" },
  { value: "closed", label: "Closed" },
  { value: "medium", label: "Medium" },
  { value: "open", label: "Open" },
];

const SYMPTOM_LIST = [
  { value: "cramps", label: "Cramps" },
  { value: "bloating", label: "Bloating" },
  { value: "breast_tenderness", label: "Breast Tenderness" },
  { value: "ovulation_pain", label: "Ovulation Pain" },
  { value: "headache", label: "Headache" },
  { value: "spotting", label: "Spotting" },
  { value: "mood_changes", label: "Mood Changes" },
  { value: "fatigue", label: "Fatigue" },
  { value: "other", label: "Other" },
];

const SEVERITY_OPTIONS = [
  { value: 1, label: "Mild" },
  { value: 2, label: "Moderate" },
  { value: 3, label: "Severe" },
];

function RadioGroup({
  name,
  options,
  value,
  onChange,
}: {
  name: string;
  options: Array<{ value: string; label: string }>;
  value: string;
  onChange: (val: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <label
          key={opt.value}
          className={`inline-flex cursor-pointer items-center rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
            value === opt.value
              ? "border-primary bg-accent text-accent-foreground"
              : "border-input bg-background text-muted-foreground hover:bg-accent/50"
          }`}
        >
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={(e) => onChange(e.target.value)}
            className="sr-only"
          />
          {opt.label}
        </label>
      ))}
    </div>
  );
}

interface EntryFormProps {
  onSubmit: (data: EntryFormData) => void;
  isSubmitting?: boolean;
}

export function EntryForm({ onSubmit, isSubmitting = false }: EntryFormProps) {
  const [date, setDate] = useState(TODAY);
  const [tempValue, setTempValue] = useState("");
  const [timeTaken, setTimeTaken] = useState("");
  const [isDiscarded, setIsDiscarded] = useState(false);
  const [discardReason, setDiscardReason] = useState("");
  const [menstrualFlow, setMenstrualFlow] = useState("");
  const [cervicalMucus, setCervicalMucus] = useState("");
  const [cervicalPosition, setCervicalPosition] = useState("");
  const [cervicalFirmness, setCervicalFirmness] = useState("");
  const [cervicalOpening, setCervicalOpening] = useState("");
  const [opkResult, setOpkResult] = useState("not_tested");
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [symptomSeverity, setSymptomSeverity] = useState(1);
  const [isPeriodStart, setIsPeriodStart] = useState(false);
  const [notes, setNotes] = useState("");
  const [cervixOpen, setCervixOpen] = useState(false);

  const toggleSymptom = (val: string) => {
    setSymptoms((prev) =>
      prev.includes(val) ? prev.filter((s) => s !== val) : [...prev, val]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      date,
      temp_value: tempValue,
      time_taken: timeTaken,
      is_discarded: isDiscarded,
      discard_reason: discardReason,
      menstrual_flow: menstrualFlow,
      cervical_mucus: cervicalMucus,
      cervical_position: cervicalPosition,
      cervical_firmness: cervicalFirmness,
      cervical_opening: cervicalOpening,
      opk_result: opkResult,
      symptoms,
      symptom_severity: symptomSeverity,
      is_period_start: isPeriodStart,
      notes,
    });
  };

  return (
    <form onSubmit={handleSubmit} aria-label="Daily entry form">
      <Card>
        <CardHeader>
          <CardTitle>Daily Entry</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="entry-date">Date</Label>
            <Input
              id="entry-date"
              type="date"
              value={date}
              max={TODAY}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="temp-value">Basal Body Temperature (°F)</Label>
            <Input
              id="temp-value"
              type="number"
              step="0.01"
              placeholder="e.g. 97.40"
              value={tempValue}
              onChange={(e) => setTempValue(e.target.value)}
              className="text-center text-3xl font-bold h-16"
              inputMode="decimal"
              aria-label="Temperature in Fahrenheit"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="time-taken">Time Taken (optional)</Label>
            <Input
              id="time-taken"
              type="time"
              value={timeTaken}
              onChange={(e) => setTimeTaken(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <label className="flex cursor-pointer items-center gap-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={isDiscarded}
                onChange={(e) => setIsDiscarded(e.target.checked)}
                className="h-4 w-4 rounded border-input"
              />
              Discard this reading
            </label>
            {isDiscarded && (
              <Input
                placeholder="Reason (e.g. illness, late waking, alcohol)"
                value={discardReason}
                onChange={(e) => setDiscardReason(e.target.value)}
                aria-label="Discard reason"
              />
            )}
          </div>

          <div className="space-y-2">
            <Label>Menstrual Flow</Label>
            <RadioGroup
              name="menstrual_flow"
              options={FLOW_OPTIONS}
              value={menstrualFlow}
              onChange={setMenstrualFlow}
            />
          </div>

          <div className="space-y-2">
            <Label>Cervical Mucus</Label>
            <RadioGroup
              name="cervical_mucus"
              options={MUCUS_OPTIONS}
              value={cervicalMucus}
              onChange={setCervicalMucus}
            />
          </div>

          <div className="space-y-2">
            <Label>OPK (Ovulation Predictor Kit)</Label>
            <RadioGroup
              name="opk_result"
              options={OPK_OPTIONS}
              value={opkResult}
              onChange={setOpkResult}
            />
          </div>

          <div className="space-y-2">
            <button
              type="button"
              onClick={() => setCervixOpen(!cervixOpen)}
              className="flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              <span>{cervixOpen ? "▾" : "▸"}</span>
              Cervical Position (optional)
            </button>
            {cervixOpen && (
              <div className="space-y-4 pl-6 pt-2">
                <div className="space-y-2">
                  <Label>Position</Label>
                  <RadioGroup
                    name="cervical_position"
                    options={POSITION_OPTIONS}
                    value={cervicalPosition}
                    onChange={setCervicalPosition}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Firmness</Label>
                  <RadioGroup
                    name="cervical_firmness"
                    options={FIRMNESS_OPTIONS}
                    value={cervicalFirmness}
                    onChange={setCervicalFirmness}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Opening</Label>
                  <RadioGroup
                    name="cervical_opening"
                    options={OPENING_OPTIONS}
                    value={cervicalOpening}
                    onChange={setCervicalOpening}
                  />
                </div>
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label>Symptoms</Label>
            <div className="flex flex-wrap gap-2">
              {SYMPTOM_LIST.map((sym) => {
                const checked = symptoms.includes(sym.value);
                return (
                  <label
                    key={sym.value}
                    className={`inline-flex cursor-pointer items-center rounded-md border px-3 py-1 text-xs font-medium transition-colors ${
                      checked
                        ? "border-primary bg-accent text-accent-foreground"
                        : "border-input bg-background text-muted-foreground hover:bg-accent/50"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleSymptom(sym.value)}
                      className="sr-only"
                    />
                    {sym.label}
                  </label>
                );
              })}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Severity</Label>
            <RadioGroup
              name="severity"
              options={SEVERITY_OPTIONS.map((o) => ({
                value: String(o.value),
                label: o.label,
              }))}
              value={String(symptomSeverity)}
              onChange={(v) => setSymptomSeverity(Number(v))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <textarea
              id="notes"
              rows={3}
              placeholder="Any other observations"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </div>

          <div className="space-y-2">
            <label className="flex cursor-pointer items-start gap-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={isPeriodStart}
                onChange={(e) => setIsPeriodStart(e.target.checked)}
                className="mt-0.5 h-4 w-4 rounded border-input"
              />
              <span>
                This is the first day of my period (starts a new cycle)
              </span>
            </label>
            {isPeriodStart && (
              <p className="text-xs text-red-600 pl-6">
                This will close the current cycle and start a new one from the selected date.
              </p>
            )}
          </div>

          <Button type="submit" className="w-full" size="lg" disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Save Entry"}
          </Button>
        </CardContent>
      </Card>
    </form>
  );
}
