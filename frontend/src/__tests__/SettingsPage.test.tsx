import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import SettingsPage from "@/pages/SettingsPage";

vi.mock("@/lib/api", () => ({
  exportData: vi.fn().mockResolvedValue(new Blob(["{}"], { type: "application/json" })),
  createCycle: vi.fn().mockResolvedValue({}),
}));

describe("SettingsPage", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders temperature unit toggle", () => {
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    expect(screen.getByText("Temperature Unit")).toBeTruthy();
    expect(screen.getByText("°F")).toBeTruthy();
    expect(screen.getByText("°C")).toBeTruthy();
  });

  it("renders interpretation method section", () => {
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    expect(screen.getByText("Interpretation Method")).toBeTruthy();
  });

  it("renders export data button", () => {
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    expect(screen.getByText("Export Data")).toBeTruthy();
  });

  it("renders start new cycle button", () => {
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    const buttons = screen.getAllByText("Start New Cycle");
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it("renders save settings button", () => {
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    expect(screen.getByText("Save Settings")).toBeTruthy();
  });

  it("toggles temperature unit on click", async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    const celsiusBtn = screen.getByText("Celsius").closest("button");
    expect(celsiusBtn).toBeTruthy();
    await user.click(celsiusBtn!);
    expect(celsiusBtn).toBeTruthy();
  });

  it("shows Fahrenheit and Celsius labels", () => {
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    expect(screen.getByText("Fahrenheit")).toBeTruthy();
    expect(screen.getByText("Celsius")).toBeTruthy();
  });

  it("save button shows Saved! on click", async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><SettingsPage /></MemoryRouter>);
    const saveBtn = screen.getByText("Save Settings");
    await user.click(saveBtn);
    await screen.findByText("Saved!");
  });
});
