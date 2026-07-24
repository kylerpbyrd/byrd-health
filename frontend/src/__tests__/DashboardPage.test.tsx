import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DashboardPage from "@/pages/DashboardPage";

vi.mock("@/hooks/useDashboard", () => ({
  useDashboard: () => ({
    data: {
      phase: "luteal" as const,
      cycle_day: 18,
      avg_cycle_length: 28,
      next_period_date: "2026-07-28",
      fertile_start_date: "2026-07-07",
      fertile_end_date: "2026-07-11",
      ovulation_date: "2026-07-09",
      ovulation_confirmed: true,
      coverline: 97.52,
      last_temp: 98.15,
      luteal_length: null,
      warnings: [
        {
          type: "info",
          message:
            "3rd cycle — data may be limited. Predictions improve with more cycles logged.",
        },
      ],
    },
    isLoading: false,
    isError: false,
  }),
  useReanalyzeInsights: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("DashboardPage", () => {
  it("renders the phase banner", async () => {
    renderWithProviders(<DashboardPage />);
    const banner = await screen.findByRole("banner");
    expect(banner).toBeInTheDocument();
  });

  it("renders stat tiles", async () => {
    renderWithProviders(<DashboardPage />);
    expect(await screen.findByText("Cycle Day")).toBeInTheDocument();
    expect(await screen.findByText("Next Period Est.")).toBeInTheDocument();
    expect(await screen.findByText("Fertile Window")).toBeInTheDocument();
    expect(await screen.findByText("Ovulation")).toBeInTheDocument();
  });

  it("renders action buttons", async () => {
    renderWithProviders(<DashboardPage />);
    expect(await screen.findByText("Log Today's Entry")).toBeInTheDocument();
    expect(await screen.findByText("View Cycle History")).toBeInTheDocument();
  });

  it("renders the BBT chart", async () => {
    renderWithProviders(<DashboardPage />);
    const chart = await screen.findByRole("img", { name: /Basal Body Temperature/i });
    expect(chart).toBeInTheDocument();
  });

  it("renders today's signs section", async () => {
    renderWithProviders(<DashboardPage />);
    expect(await screen.findByText("Today's Signs")).toBeInTheDocument();
  });
});
