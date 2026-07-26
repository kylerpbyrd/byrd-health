import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProfilesPage from "@/pages/ProfilesPage";
import { fetchProfiles } from "@/lib/api";

vi.mock("@/lib/api", () => ({
  fetchProfiles: vi.fn(),
  createProfile: vi.fn(),
  deleteProfile: vi.fn(),
  activateProfile: vi.fn(),
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ProfilesPage", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders create profile card title", () => {
    vi.mocked(fetchProfiles).mockReturnValue(new Promise(() => {}));
    render(<ProfilesPage />, { wrapper });
    expect(screen.getByText("Create Profile")).toBeTruthy();
  });

  it("shows profiles section header", () => {
    vi.mocked(fetchProfiles).mockReturnValue(new Promise(() => {}));
    render(<ProfilesPage />, { wrapper });
    expect(screen.getByText("Profiles")).toBeTruthy();
  });

  it("shows profiles section with no items for empty list", async () => {
    vi.mocked(fetchProfiles).mockResolvedValue([]);
    render(<ProfilesPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Profiles")).toBeTruthy();
    });
  });

  it("renders profile list", async () => {
    vi.mocked(fetchProfiles).mockResolvedValue([
      { id: "p1", name: "Test Profile", slug: "test", temp_unit: "F", interpretation_method: "standard", is_active: true, created_at: "2026-01-01T00:00:00Z" },
    ]);
    render(<ProfilesPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText("Test Profile")).toBeTruthy();
    });
  });

  it("displays temp unit and interpretation method", async () => {
    vi.mocked(fetchProfiles).mockResolvedValue([
      { id: "p1", name: "Test Profile", slug: "test", temp_unit: "C", interpretation_method: "conservative", is_active: true, created_at: "2026-01-01T00:00:00Z" },
    ]);
    render(<ProfilesPage />, { wrapper });
    await waitFor(() => {
      expect(screen.getByText(/C \/ Conservative/)).toBeTruthy();
    });
  });

  it("has create profile input field", () => {
    vi.mocked(fetchProfiles).mockReturnValue(new Promise(() => {}));
    render(<ProfilesPage />, { wrapper });
    expect(screen.getByLabelText("Profile Name")).toBeTruthy();
  });
});
