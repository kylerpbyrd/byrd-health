import { AlertTriangle, Info } from "lucide-react";

interface WarningBannerProps {
  type: "warning" | "info";
  message: string;
}

export function WarningBanner({ type, message }: WarningBannerProps) {
  const isWarning = type === "warning";
  return (
    <div
      role="alert"
      className={`mb-4 flex items-start gap-3 rounded-lg border p-4 text-sm ${
        isWarning
          ? "border-amber-300 bg-amber-50 text-amber-900"
          : "border-blue-300 bg-blue-50 text-blue-900"
      }`}
    >
      {isWarning ? (
        <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
      ) : (
        <Info className="mt-0.5 h-4 w-4 flex-shrink-0 text-blue-600" />
      )}
      <span>{message}</span>
    </div>
  );
}
