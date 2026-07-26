import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { Skeleton, StatTileSkeleton, ChartSkeleton, CardSkeleton } from "@/components/Skeleton";

describe("Skeleton", () => {
  it("renders with default classes", () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toHaveClass("animate-pulse");
  });

  it("merges custom className", () => {
    const { container } = render(<Skeleton className="h-10" />);
    expect(container.firstChild).toHaveClass("h-10");
  });

  it("retains default classes with custom className", () => {
    const { container } = render(<Skeleton className="h-10" />);
    expect(container.firstChild).toHaveClass("animate-pulse");
    expect(container.firstChild).toHaveClass("rounded-md");
  });
});

describe("StatTileSkeleton", () => {
  it("renders without crashing", () => {
    const { container } = render(<StatTileSkeleton />);
    expect(container.firstChild).toBeTruthy();
  });

  it("has border class", () => {
    const { container } = render(<StatTileSkeleton />);
    expect(container.firstChild).toHaveClass("rounded-lg");
    expect(container.firstChild).toHaveClass("border");
  });
});

describe("ChartSkeleton", () => {
  it("renders without crashing", () => {
    const { container } = render(<ChartSkeleton />);
    expect(container.firstChild).toBeTruthy();
  });

  it("contains multiple skeleton elements", () => {
    const { container } = render(<ChartSkeleton />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThanOrEqual(2);
  });
});

describe("CardSkeleton", () => {
  it("renders without crashing", () => {
    const { container } = render(<CardSkeleton />);
    expect(container.firstChild).toBeTruthy();
  });

  it("has space-y-3 class for layout", () => {
    const { container } = render(<CardSkeleton />);
    expect(container.firstChild).toHaveClass("space-y-3");
  });
});
