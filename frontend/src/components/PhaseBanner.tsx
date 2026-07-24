import type { CyclePhase } from "@/types/fertility";
import { cyclePhaseLabel } from "@/lib/utils";

const phaseColors: Record<CyclePhase, string> = {
  menstruation: "bg-red-500",
  pre_ovulatory: "bg-blue-400",
  fertile: "bg-green-500",
  ovulation: "bg-orange-400",
  luteal: "bg-purple-500",
  unknown: "bg-gray-400",
};

interface PhaseBannerProps {
  phase: CyclePhase;
  cycleDay: number;
  avgCycleLength: number | null;
}

export function PhaseBanner({ phase, cycleDay, avgCycleLength }: PhaseBannerProps) {
  return (
    <div
      className={`mb-6 rounded-lg p-4 text-white ${phaseColors[phase]}`}
      role="banner"
      aria-label={`Current phase: ${cyclePhaseLabel(phase)}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold">{cyclePhaseLabel(phase)}</h2>
          <p className="text-sm opacity-90">
            Cycle Day <strong>{cycleDay}</strong>
            {avgCycleLength ? ` of ~${avgCycleLength} days` : ""}
          </p>
        </div>
      </div>
    </div>
  );
}
