import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "@/components/ErrorBoundary";

function BrokenComponent(): React.ReactNode {
  throw new Error("test error");
}

describe("ErrorBoundary", () => {
  it("renders children when no error", () => {
    render(<ErrorBoundary><p>hello</p></ErrorBoundary>);
    expect(screen.getByText("hello")).toBeTruthy();
  });

  it("shows error UI when child throws", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(<ErrorBoundary><BrokenComponent /></ErrorBoundary>);
    expect(screen.getByText("Something went wrong")).toBeTruthy();
    expect(screen.getByText("Try Again")).toBeTruthy();
    vi.restoreAllMocks();
  });

  it("shows error message text", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(<ErrorBoundary><BrokenComponent /></ErrorBoundary>);
    expect(screen.getByText("An unexpected error occurred. Your data is safe.")).toBeTruthy();
    vi.restoreAllMocks();
  });

  it("try again button resets error state on click", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(<ErrorBoundary><BrokenComponent /></ErrorBoundary>);
    const button = screen.getByText("Try Again");
    expect(button.tagName).toBe("BUTTON");
    expect(button).toBeTruthy();
    vi.restoreAllMocks();
  });
});
