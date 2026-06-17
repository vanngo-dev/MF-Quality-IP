import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ErrorState } from "../components/ui/ErrorState";
import { LoadingState } from "../components/ui/LoadingState";
import { StatusBadge, type StatusValue } from "../components/ui/StatusBadge";

describe("StatusBadge", () => {
  it("renders supported status labels", () => {
    const statuses: StatusValue[] = [
      "open",
      "acknowledged",
      "investigating",
      "contained",
      "resolved",
      "draft",
      "active",
      "waiting_on_data",
    ];

    render(
      <>
        {statuses.map((status) => (
          <StatusBadge key={status} status={status} />
        ))}
      </>,
    );

    expect(screen.getByText("Open")).toBeInTheDocument();
    expect(screen.getByText("Acknowledged")).toBeInTheDocument();
    expect(screen.getByText("Investigating")).toBeInTheDocument();
    expect(screen.getByText("Contained")).toBeInTheDocument();
    expect(screen.getByText("Resolved")).toBeInTheDocument();
    expect(screen.getByText("Draft")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByText("Waiting on Data")).toBeInTheDocument();
  });

  it("renders loading and error states", () => {
    render(
      <>
        <LoadingState />
        <ErrorState />
      </>,
    );

    expect(screen.getByText("Loading manufacturing quality data...")).toBeInTheDocument();
    expect(screen.getByText("Unable to load manufacturing quality data.")).toBeInTheDocument();
  });
});
