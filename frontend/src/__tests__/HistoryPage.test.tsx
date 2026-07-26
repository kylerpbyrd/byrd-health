import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import HistoryPage from "@/pages/HistoryPage";
import { fetchCycles } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  fetchCycles: vi.fn(),
  createCycle: vi.fn(),
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("HistoryPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows the page title when loading", () => {
    vi.mocked(fetchCycles).mockReturnValue(new Promise(() => {}));
    render(<HistoryPage />, { wrapper });
    expect(screen.getByText("Cycle History")).toBeTruthy();
  });

  it("renders dashboard back link", () => {
    vi.mocked(fetchCycles).mockResolvedValue([]);
    render(<HistoryPage />, { wrapper });
    expect(screen.getByText("← Dashboard")).toBeTruthy();
  });

  it("shows error state", async () => {
    vi.mocked(fetchCycles).mockRejectedValue(new Error("fail"));
    render(<HistoryPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText(/No cycles found/)).toBeTruthy();
    });
  });

  it("renders cycles when data loads", async () => {
    vi.mocked(fetchCycles).mockResolvedValue([
      { id: "c1", start_date: "2026-01-01", end_date: "2026-01-28", cycle_length: 28, ovulation_date: "2026-01-14", ovulation_confirmed: true, luteal_length: 14, is_active: false },
      { id: "c2", start_date: "2026-01-30", end_date: null, cycle_length: null, ovulation_date: null, ovulation_confirmed: false, luteal_length: null, is_active: true },
    ]);
    render(<HistoryPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("28 days")).toBeTruthy();
      expect(screen.getByText("Active")).toBeTruthy();
    });
  });

  it("renders table with no rows for empty cycles list", async () => {
    vi.mocked(fetchCycles).mockResolvedValue([]);
    render(<HistoryPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Cycle")).toBeTruthy();
      expect(screen.getByText("Start Date")).toBeTruthy();
    });
  });

  it("shows active badge for active cycle", async () => {
    vi.mocked(fetchCycles).mockResolvedValue([
      { id: "c1", start_date: "2026-01-30", end_date: null, cycle_length: null, ovulation_date: null, ovulation_confirmed: false, luteal_length: null, is_active: true },
    ]);
    render(<HistoryPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Active")).toBeTruthy();
    });
  });
});
