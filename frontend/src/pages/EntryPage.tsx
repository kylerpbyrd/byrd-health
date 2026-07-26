import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { EntryForm } from "@/components/EntryForm";
import type { EntryFormData } from "@/types/fertility";
import { createEntry } from "@/lib/api";

export default function EntryPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: EntryFormData) => {
    setIsSubmitting(true);
    try {
      await createEntry(data);
      toast.success("Entry saved successfully!");
      setTimeout(() => navigate("/"), 1500);
    } catch {
      toast.error("Failed to save entry. Please try again.");
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

      <EntryForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
    </div>
  );
}
