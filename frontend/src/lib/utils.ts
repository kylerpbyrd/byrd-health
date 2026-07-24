import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatShortDate(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export function formatTemp(value: number, unit: "F" | "C"): string {
  return `${value.toFixed(2)}°${unit}`;
}

export function cyclePhaseLabel(phase: string): string {
  const labels: Record<string, string> = {
    menstruation: "Menstruation",
    pre_ovulatory: "Pre-Ovulatory",
    fertile: "Fertile Window",
    ovulation: "Ovulation",
    luteal: "Luteal Phase",
    unknown: "Unknown",
  };
  return labels[phase] || phase.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
