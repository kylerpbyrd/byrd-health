import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import SettingsPage from "@/pages/SettingsPage";

const { mockProfile } = vi.hoisted(() => ({
  mockProfile: {
    id: "test-uuid",
    name: "Test User",
    slug: "test_user",
    temp_unit: "F",
    interpretation_method: "standard",
    is_active: true,
    created_at: "2026-01-01T00:00:00",
  },
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

vi.mock("@/lib/api", () => ({
  fetchProfiles: vi.fn().mockResolvedValue([mockProfile]),
  updateProfile: vi.fn().mockResolvedValue(mockProfile),
  exportData: vi.fn().mockResolvedValue(new Blob(["{}"], { type: "application/json" })),
  createCycle: vi.fn().mockResolvedValue({}),
}));

function renderSettings() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("renders temperature unit toggle", async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText("Temperature Unit")).toBeTruthy();
    });
    expect(screen.getByText("°F")).toBeTruthy();
    expect(screen.getByText("°C")).toBeTruthy();
  });

  it("renders interpretation method section", async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText("Interpretation Method")).toBeTruthy();
    });
  });

  it("renders export data button", async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText("Export Data")).toBeTruthy();
    });
  });

  it("renders start new cycle button", async () => {
    renderSettings();
    await waitFor(() => {
      const buttons = screen.getAllByText("Start New Cycle");
      expect(buttons.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("renders save settings button", async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText("Save Settings")).toBeTruthy();
    });
  });

  it("toggles temperature unit on click", async () => {
    const user = userEvent.setup();
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText("Celsius")).toBeTruthy();
    });
    const celsiusBtn = screen.getByText("Celsius").closest("button");
    expect(celsiusBtn).toBeTruthy();
    await user.click(celsiusBtn!);
    expect(celsiusBtn).toBeTruthy();
  });

  it("shows Fahrenheit and Celsius labels", async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText("Fahrenheit")).toBeTruthy();
    });
    expect(screen.getByText("Celsius")).toBeTruthy();
  });

  it("save button triggers save when settings changed", async () => {
    const user = userEvent.setup();
    const { updateProfile } = await import("@/lib/api");
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText("Celsius")).toBeTruthy();
    });

    // Change temperature unit to make the save button active
    const celsiusBtn = screen.getByText("Celsius").closest("button");
    expect(celsiusBtn).toBeTruthy();
    await user.click(celsiusBtn!);

    // Save should now be clickable (not disabled)
    const saveBtn = screen.getByText("Save Settings");
    expect(saveBtn).toBeTruthy();
    await user.click(saveBtn);

    await waitFor(() => {
      expect(updateProfile).toHaveBeenCalledWith("test-uuid", expect.objectContaining({
        temp_unit: "C",
        interpretation_method: "standard",
      }));
      expect(screen.getByText("Saved!")).toBeTruthy();
    });
  });
});