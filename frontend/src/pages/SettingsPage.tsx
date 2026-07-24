import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Download, RefreshCw, AlertTriangle, Loader2 } from "lucide-react";
import { exportData, createCycle } from "@/lib/api";

export default function SettingsPage() {
  const [tempUnit, setTempUnit] = useState("F");
  const [method, setMethod] = useState("standard");
  const [saved, setSaved] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [startingCycle, setStartingCycle] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
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

  const handleNewCycle = async () => {
    setStartingCycle(true);
    try {
      await createCycle();
      alert("New cycle started successfully.");
    } catch {
      alert("Failed to start a new cycle. Make sure the backend is running.");
    } finally {
      setStartingCycle(false);
    }
  };

  return (
    <div className="space-y-6">
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
              onClick={() => setTempUnit("F")}
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
              onClick={() => setTempUnit("C")}
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
            onChange={(e) => setMethod(e.target.value)}
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
          <Button
            onClick={handleNewCycle}
            variant="destructive"
            disabled={startingCycle}
          >
            {startingCycle ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Start New Cycle
          </Button>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave}>
          {saved ? "Saved!" : "Save Settings"}
        </Button>
      </div>
    </div>
  );
}
