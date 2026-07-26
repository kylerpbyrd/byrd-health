import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PhaseBanner } from "@/components/PhaseBanner";
import type { CyclePhase } from "@/types/fertility";

describe("PhaseBanner", () => {
  const phases: CyclePhase[] = [
    "menstruation",
    "pre_ovulatory",
    "fertile",
    "ovulation",
    "luteal",
    "unknown",
  ];

  for (const phase of phases) {
    it(`displays correct phase name for ${phase}`, () => {
      render(<PhaseBanner phase={phase} cycleDay={14} avgCycleLength={28} />);
      const labels: Record<CyclePhase, string> = {
        menstruation: "Menstruation",
        pre_ovulatory: "Pre-Ovulatory",
        fertile: "Fertile Window",
        ovulation: "Ovulation",
        luteal: "Luteal Phase",
        unknown: "Unknown",
      };
      expect(screen.getByText(labels[phase])).toBeInTheDocument();
    });
  }

  it("displays cycle day", () => {
    render(<PhaseBanner phase="luteal" cycleDay={18} avgCycleLength={28} />);
    expect(screen.getByText(/Cycle Day/)).toBeInTheDocument();
    expect(screen.getByText("18")).toBeInTheDocument();
  });

  it("displays average cycle length when provided", () => {
    render(<PhaseBanner phase="luteal" cycleDay={18} avgCycleLength={28} />);
    expect(screen.getByText(/of ~28 days/)).toBeInTheDocument();
  });

  it("does not show cycle length when null", () => {
    render(<PhaseBanner phase="unknown" cycleDay={5} avgCycleLength={null} />);
    expect(screen.queryByText(/of ~/)).not.toBeInTheDocument();
  });

  it("has correct ARIA role and label", () => {
    render(<PhaseBanner phase="menstruation" cycleDay={3} avgCycleLength={28} />);
    const banner = screen.getByRole("status");
    expect(banner).toHaveAttribute("aria-label", "Current phase: Menstruation");
  });
});
