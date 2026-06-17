import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DashboardPage } from "../features/dashboard/DashboardPage";

describe("DashboardPage", () => {
  it("displays mock stat cards", () => {
    render(<DashboardPage />);

    expect(screen.getByText("Total Vehicles")).toBeInTheDocument();
    expect(screen.getByText("Open Defects")).toBeInTheDocument();
    expect(screen.getByText("Open Alerts")).toBeInTheDocument();
    expect(screen.getByText("Critical Alerts")).toBeInTheDocument();
  });
});
