import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Download, RefreshCw, AlertTriangle, Loader2, Save, Calendar } from "lucide-react";
import { exportData, createCycle } from "@/lib/api";
import { useActiveProfile, useUpdateProfile } from "@/hooks/useProfile";
import type { TempUnit, InterpretationMethod } from "@/types/fertility";

export default function SettingsPage() {
  const { activeProfile, isLoading } = useActiveProfile();
  const updateMutation = useUpdateProfile();

  const [tempUnit, setTempUnit] = useState<TempUnit>("F");
  const [method, setMethod] = useState<InterpretationMethod>("standard");
  const [saved, setSaved] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [startingCycle, setStartingCycle] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [newCycleDate, setNewCycleDate] = useState(new Date().toISOString().slice(0, 10));

  // Sync local state from active profile on load or profile change
  useEffect(() => {
    if (activeProfile) {
      setTempUnit(activeProfile.temp_unit as TempUnit);
      setMethod(activeProfile.interpretation_method as InterpretationMethod);
      setDirty(false);
    }
  }, [activeProfile?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleTempUnitChange = (unit: TempUnit) => {
    setTempUnit(unit);
    setDirty(true);
    setSaved(false);
  };

  const handleMethodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setMethod(e.target.value as InterpretationMethod);
    setDirty(true);
    setSaved(false);
  };

  const handleSave = async () => {
    if (!activeProfile) return;
    try {
      await updateMutation.mutateAsync({
        profileId: activeProfile.id,
        data: {
          temp_unit: tempUnit,
          interpretation_method: method,
        },
      });
      setDirty(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // Error handled by React Query; toast shown via mutation state
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await exportData();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `byrd-health-export-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      alert("Failed to export data. Make sure the backend is running.");
    } finally {
      setExporting(false);
    }
  };

  const handleNewCycle = () => {
    setNewCycleDate(new Date().toISOString().slice(0, 10));
    setShowDatePicker(true);
  };

  const handleConfirmNewCycle = async () => {
    setStartingCycle(true);
    try {
      await createCycle(newCycleDate);
      setShowDatePicker(false);
      alert("New cycle started successfully.");
    } catch {
      alert("Failed to start a new cycle. Make sure the backend is running.");
    } finally {
      setStartingCycle(false);
    }
  };

  const handleCancelNewCycle = () => {
    setShowDatePicker(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!activeProfile) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <AlertTriangle className="h-12 w-12 mb-4" />
        <p className="text-lg">No active profile found.</p>
        <p className="text-sm">Create a profile in the Profiles page first.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {updateMutation.isError && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          Failed to save settings. Please try again.
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Temperature Unit</CardTitle>
          <CardDescription>
            Choose between Fahrenheit and Celsius for temperature display.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <button
              onClick={() => handleTempUnitChange("F")}
              className={`flex-1 rounded-lg border px-4 py-3 text-center font-medium transition-colors ${
                tempUnit === "F"
                  ? "border-primary bg-accent text-accent-foreground"
                  : "border-input hover:bg-accent/50"
              }`}
            >
              <span className="block text-xl">°F</span>
              <span className="text-xs text-muted-foreground">Fahrenheit</span>
            </button>
            <button
              onClick={() => handleTempUnitChange("C")}
              className={`flex-1 rounded-lg border px-4 py-3 text-center font-medium transition-colors ${
                tempUnit === "C"
                  ? "border-primary bg-accent text-accent-foreground"
                  : "border-input hover:bg-accent/50"
              }`}
            >
              <span className="block text-xl">°C</span>
              <span className="text-xs text-muted-foreground">Celsius</span>
            </button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Interpretation Method</CardTitle>
          <CardDescription>
            Standard uses FAM rules. Conservative requires more confirmation for ovulation detection.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            value={method}
            onChange={handleMethodChange}
            options={[
              { value: "standard", label: "Standard (FAM rules)" },
              { value: "conservative", label: "Conservative (stricter confirmation)" },
            ]}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Data Export</CardTitle>
          <CardDescription>
            Download all your fertility data as a JSON file.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleExport}
            variant="outline"
            className="w-full sm:w-auto"
            disabled={exporting}
          >
            {exporting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Download className="mr-2 h-4 w-4" />
            )}
            Export Data
          </Button>
        </CardContent>
      </Card>

      <Card className="border-destructive/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Start New Cycle
          </CardTitle>
          <CardDescription>
            This will close the current cycle and start a new one. Only use this if you are certain a new cycle has begun.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {showDatePicker ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <input
                  type="date"
                  value={newCycleDate}
                  onChange={(e) => setNewCycleDate(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleConfirmNewCycle}
                  variant="destructive"
                  disabled={startingCycle}
                >
                  {startingCycle ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : null}
                  Confirm
                </Button>
                <Button
                  onClick={handleCancelNewCycle}
                  variant="outline"
                  disabled={startingCycle}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <Button
              onClick={handleNewCycle}
              variant="destructive"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Start New Cycle
            </Button>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={!dirty || updateMutation.isPending}
        >
          {updateMutation.isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : saved ? (
            <Save className="mr-2 h-4 w-4" />
          ) : null}
          {updateMutation.isPending ? "Saving..." : saved ? "Saved!" : "Save Settings"}
        </Button>
      </div>
    </div>
  );
}