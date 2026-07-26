import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { EntryForm } from "@/components/EntryForm";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { EntryFormData } from "@/types/fertility";
import { createEntry } from "@/lib/api";

export default function EntryPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deviceTemp, setDeviceTemp] = useState<number | null>(null);
  const [deviceName, setDeviceName] = useState<string>("");

  useWebSocket({
    onDeviceReading: (reading) => {
      setDeviceTemp(reading.payload.data.temperature);
      setDeviceName(reading.payload.data.device_type);
    },
  });

  const handleSubmit = async (data: EntryFormData) => {
    setIsSubmitting(true);
    try {
      await createEntry(data);
      toast.success("Entry saved successfully!");
      setTimeout(() => navigate("/"), 1500);
    } catch (error) {
      console.error("Entry submission failed:", error);

      const err = error as any;
      if (typeof err?.status === "number") {
        const body = err.message || "";
        console.error("Response body:", body);

        switch (err.status) {
          case 422:
            toast.error("Validation error. Check your temperature value.");
            break;
          case 404:
            toast.error("No active profile found. Please create a profile first.");
            break;
          case 500:
            toast.error("Server error. Check add-on logs.");
            break;
          default:
            toast.error(`Failed to save entry. (${err.status})`);
        }
      } else {
        console.error("Network error:", err.message);
        toast.error("Cannot reach server. Check add-on is running.");
      }
    } finally {
      setIsSubmitting(false);
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

      <EntryForm
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
        deviceTemp={deviceTemp}
        deviceName={deviceName}
      />
    </div>
  );
}
