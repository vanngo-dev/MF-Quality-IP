import { screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { vi } from "vitest";

import { DashboardPage } from "../features/dashboard/DashboardPage";
import { mockApiFailure, mockApiResponses, renderWithQueryClient } from "./testUtils";

describe("DashboardPage", () => {
  it("renders a loading state while live metrics are loading", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => undefined)));

    renderWithQueryClient(<DashboardPage />);

    expect(screen.getByText("Loading dashboard metrics...")).toBeInTheDocument();
  });

  it("renders an error state when the backend API fails", async () => {
    mockApiFailure();

    renderWithQueryClient(<DashboardPage />);

    expect(await screen.findByText("Unable to load dashboard data from the backend API.")).toBeInTheDocument();
  });

  it("displays live stat cards from mocked API responses", async () => {
    mockApiResponses();

    renderWithQueryClient(<DashboardPage />);

    expect(await screen.findByText("Total Vehicles")).toBeInTheDocument();
    expectMetric("Total Vehicles", "2");
    expectMetric("Open Defects", "1");
    expectMetric("Open Alerts", "1");
    expectMetric("Critical Alerts", "1");
    expectMetric("Top Defect Station", "ST-TORQUE");
    expectMetric("Latest Sensor Event", "Not available yet");
    expect(screen.getByText("Repeated torque defects")).toBeInTheDocument();
  });
});

function expectMetric(title: string, value: string) {
  const card = screen.getByText(title).closest("article");

  expect(card).not.toBeNull();
  expect(within(card as HTMLElement).getByText(value)).toBeInTheDocument();
}
