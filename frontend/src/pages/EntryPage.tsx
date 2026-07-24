import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { EntryForm } from "@/components/EntryForm";
import type { EntryFormData } from "@/types/fertility";
import { createEntry } from "@/lib/api";

export default function EntryPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (data: EntryFormData) => {
    setIsSubmitting(true);
    setMessage(null);
    try {
      await createEntry(data);
      setMessage("Entry saved successfully!");
      setTimeout(() => navigate("/"), 1500);
    } catch {
      setMessage("Failed to save entry. Please try again.");
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

      {message && (
        <div
          className={`mb-4 rounded-lg border p-3 text-sm ${
            message.includes("success")
              ? "border-green-300 bg-green-50 text-green-900"
              : "border-red-300 bg-red-50 text-red-900"
          }`}
          role="alert"
        >
          {message}
        </div>
      )}

      <EntryForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
    </div>
  );
}
