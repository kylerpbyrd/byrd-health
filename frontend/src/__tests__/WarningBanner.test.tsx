import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { WarningBanner } from "@/components/WarningBanner";

describe("WarningBanner", () => {
  it("renders the message text", () => {
    render(<WarningBanner type="info" message="Test message" />);
    expect(screen.getByText("Test message")).toBeTruthy();
  });

  it("has alert role", () => {
    render(<WarningBanner type="info" message="Test" />);
    expect(screen.getByRole("alert")).toBeTruthy();
  });

  it("applies info styling for info type", () => {
    render(<WarningBanner type="info" message="Info message" />);
    const alert = screen.getByRole("alert");
    expect(alert).toHaveClass("border-blue-300");
    expect(alert).toHaveClass("bg-blue-50");
  });

  it("applies warning styling for warning type", () => {
    render(<WarningBanner type="warning" message="Warning message" />);
    const alert = screen.getByRole("alert");
    expect(alert).toHaveClass("border-amber-300");
    expect(alert).toHaveClass("bg-amber-50");
  });
});
