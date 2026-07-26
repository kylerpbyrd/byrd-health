import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Layout } from "@/components/Layout";

describe("Layout", () => {
  it("renders the app title", () => {
    render(<MemoryRouter><Layout><p>content</p></Layout></MemoryRouter>);
    expect(screen.getByText("Byrd Health")).toBeTruthy();
  });

  it("renders children", () => {
    render(<MemoryRouter><Layout><p>test content</p></Layout></MemoryRouter>);
    expect(screen.getByText("test content")).toBeTruthy();
  });

  it("renders all nav links", () => {
    render(<MemoryRouter><Layout><p /></Layout></MemoryRouter>);
    expect(screen.getByLabelText("Dashboard")).toBeTruthy();
    expect(screen.getByLabelText("Log Entry")).toBeTruthy();
    expect(screen.getByLabelText("History")).toBeTruthy();
    expect(screen.getByLabelText("Profiles")).toBeTruthy();
    expect(screen.getByLabelText("Settings")).toBeTruthy();
  });

  it("has skip to content link", () => {
    render(<MemoryRouter><Layout><p /></Layout></MemoryRouter>);
    expect(screen.getByText("Skip to content")).toBeTruthy();
  });

  it("main element has correct id", () => {
    render(<MemoryRouter><Layout><p /></Layout></MemoryRouter>);
    expect(document.getElementById("main-content")).toBeTruthy();
  });

  it("has header with sticky class", () => {
    render(<MemoryRouter><Layout><p /></Layout></MemoryRouter>);
    const header = document.querySelector("header");
    expect(header).toBeTruthy();
    expect(header).toHaveClass("sticky");
  });

  it("renders Activity icon as decorative", () => {
    render(<MemoryRouter><Layout><p /></Layout></MemoryRouter>);
    const icon = document.querySelector("svg.lucide-activity");
    expect(icon).toBeTruthy();
    expect(icon).toHaveAttribute("aria-hidden", "true");
  });
});
