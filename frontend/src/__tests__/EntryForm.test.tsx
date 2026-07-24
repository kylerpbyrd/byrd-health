import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { EntryForm } from "@/components/EntryForm";

describe("EntryForm", () => {
  it("renders all form fields", () => {
    render(<EntryForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/Temperature/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Date")).toBeInTheDocument();
    expect(screen.getByLabelText(/Time Taken/i)).toBeInTheDocument();
    expect(screen.getByText("Menstrual Flow")).toBeInTheDocument();
    expect(screen.getByText("Cervical Mucus")).toBeInTheDocument();
    expect(screen.getByText(/OPK/)).toBeInTheDocument();
    expect(screen.getByText("Symptoms")).toBeInTheDocument();
    expect(screen.getByText("Severity")).toBeInTheDocument();
    expect(screen.getByLabelText("Notes")).toBeInTheDocument();
  });

  it("validates temperature input", async () => {
    const onSubmit = vi.fn();
    render(<EntryForm onSubmit={onSubmit} />);

    const tempInput = screen.getByLabelText(/Temperature/i);
    expect(tempInput).toHaveAttribute("type", "number");
    expect(tempInput).toHaveAttribute("step", "0.01");

    await userEvent.type(tempInput, "97.40");
    expect(tempInput).toHaveValue(97.4);
  });

  it("renders the save button", () => {
    render(<EntryForm onSubmit={vi.fn()} />);
    expect(screen.getByRole("button", { name: /Save Entry/i })).toBeInTheDocument();
  });

  it("shows discard reason field when discard is checked", async () => {
    const user = userEvent.setup();
    render(<EntryForm onSubmit={vi.fn()} />);

    const discardCheckbox = screen.getByLabelText(/Discard this reading/i);
    await user.click(discardCheckbox);

    expect(screen.getByLabelText(/Discard reason/i)).toBeInTheDocument();
  });

  it("renders cervical position section toggle", () => {
    render(<EntryForm onSubmit={vi.fn()} />);
    expect(screen.getByText(/Cervical Position/i)).toBeInTheDocument();
  });

  it("calls onSubmit with form data", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<EntryForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/Temperature/i), "97.40");
    await user.click(screen.getByRole("button", { name: /Save Entry/i }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        temp_value: "97.4",
        is_discarded: false,
        is_period_start: false,
        opk_result: "not_tested",
        symptom_severity: 1,
        symptoms: [],
      })
    );
  });
});
