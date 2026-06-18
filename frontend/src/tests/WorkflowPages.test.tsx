import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "../app/App";
import { createAppTestRouter } from "../app/router";
import { EvidencePanel } from "../features/investigations/components/EvidencePanel";
import { TimelinePanel } from "../features/investigations/components/TimelinePanel";
import { mockApiResponses } from "./testUtils";

function renderApp(initialRoute: string) {
  return render(<App router={createAppTestRouter([initialRoute])} />);
}

describe("Phase 11 workflow pages", () => {
  it("renders alert detail data", async () => {
    mockApiResponses();

    renderApp("/alerts/1");

    expect((await screen.findAllByRole("heading", { name: "Repeated torque defects" })).length).toBeGreaterThan(0);
    expect(screen.getByText("REPEATED_DEFECT_STATION")).toBeInTheDocument();
    expect(screen.getByText("Multiple torque defects detected at the station")).toBeInTheDocument();
    expect(screen.getByText("ST-TORQUE")).toBeInTheDocument();
  });

  it("renders the alert evidence panel", async () => {
    mockApiResponses();

    renderApp("/alerts/1");

    expect(await screen.findByLabelText("Alert Evidence")).toBeInTheDocument();
    expect(screen.getByText(/defect_count/i)).toBeInTheDocument();
  });

  it("renders the create investigation form from alert detail", async () => {
    mockApiResponses({ "GET /api/v1/investigations": [] });

    renderApp("/alerts/1");

    fireEvent.click(await screen.findByRole("button", { name: "Create Investigation" }));

    expect(screen.getByLabelText("Title")).toBeInTheDocument();
    expect(screen.getByLabelText("Summary")).toBeInTheDocument();
    expect(screen.getByLabelText("Root-cause hypothesis")).toBeInTheDocument();
  });

  it("calls create investigation mutation", async () => {
    const fetchMock = mockApiResponses({ "GET /api/v1/investigations": [] });

    renderApp("/alerts/1");

    fireEvent.click(await screen.findByRole("button", { name: "Create Investigation" }));
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Investigate torque defects" } });
    fireEvent.change(screen.getByLabelText("Summary"), { target: { value: "Initial review" } });
    fireEvent.change(screen.getByLabelText("Root-cause hypothesis"), {
      target: { value: "Torque tool drift" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save Investigation" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/alerts/1/investigation",
        expect.objectContaining({
          body: JSON.stringify({
            title: "Investigate torque defects",
            summary: "Initial review",
            root_cause_hypothesis: "Torque tool drift",
            status: "active",
          }),
          method: "POST",
        }),
      );
    });
  });

  it("renders investigation detail data", async () => {
    mockApiResponses();

    renderApp("/investigations/1");

    expect((await screen.findAllByRole("heading", { name: "Investigate repeated torque defects" })).length).toBeGreaterThan(0);
    expect(screen.getByText("Torque tool may be drifting out of calibration")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Generate AI Summary" })).toBeInTheDocument();
  });

  it("updates investigation summary and root-cause hypothesis", async () => {
    const fetchMock = mockApiResponses();

    renderApp("/investigations/1");

    await screen.findAllByRole("heading", { name: "Investigate repeated torque defects" });
    fireEvent.change(screen.getByLabelText("Summary"), { target: { value: "Updated summary" } });
    fireEvent.change(screen.getByLabelText("Root-cause hypothesis"), { target: { value: "Updated hypothesis" } });
    fireEvent.click(screen.getByRole("button", { name: "Save Changes" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/investigations/1",
        expect.objectContaining({
          body: JSON.stringify({
            title: "Investigate repeated torque defects",
            summary: "Updated summary",
            root_cause_hypothesis: "Updated hypothesis",
            status: "draft",
          }),
          method: "PATCH",
        }),
      );
    });
  });

  it("updates investigation status", async () => {
    const fetchMock = mockApiResponses();

    renderApp("/investigations/1");

    fireEvent.click(await screen.findByRole("button", { name: "Resolve Investigation" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/investigations/1/status",
        expect.objectContaining({
          body: JSON.stringify({ status: "resolved" }),
          method: "PATCH",
        }),
      );
    });
  });

  it("renders JSON evidence directly", () => {
    render(<EvidencePanel evidence={{ defect_count: 5, window_minutes: 30 }} />);

    expect(screen.getByText(/defect_count/i)).toBeInTheDocument();
    expect(screen.getByText(/window_minutes/i)).toBeInTheDocument();
  });

  it("renders timeline items", () => {
    render(<TimelinePanel items={[{ label: "Alert created", timestamp: "2026-06-09T12:10:00Z" }]} />);

    expect(screen.getByText("Alert created")).toBeInTheDocument();
  });

  it("routes search result links to alert detail", async () => {
    mockApiResponses();

    renderApp("/search");

    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "torque" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));
    fireEvent.click(await screen.findByRole("link", { name: "Open Alerts" }));

    expect((await screen.findAllByRole("heading", { name: "Low vision confidence" })).length).toBeGreaterThan(0);
  });

  it("shows the Generate AI Summary button", async () => {
    mockApiResponses();

    renderApp("/investigations/1");

    expect(await screen.findByRole("button", { name: "Generate AI Summary" })).toBeInTheDocument();
  });

  it("clicking Generate AI Summary calls the API mutation", async () => {
    const fetchMock = mockApiResponses();

    renderApp("/investigations/1");

    fireEvent.click(await screen.findByRole("button", { name: "Generate AI Summary" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/investigations/1/ai-summary",
        expect.objectContaining({
          body: JSON.stringify({}),
          method: "POST",
        }),
      );
    });
  });

  it("shows loading state while generating an AI summary", async () => {
    const fetchMock = mockApiResponses();

    renderApp("/investigations/1");

    const button = await screen.findByRole("button", { name: "Generate AI Summary" });
    fetchMock.mockImplementationOnce(() => new Promise<Response>(() => undefined));
    fireEvent.click(button);

    expect(await screen.findByText("Generating AI summary...")).toBeInTheDocument();
  });

  it("renders AI summary fields after generation", async () => {
    mockApiResponses();

    renderApp("/investigations/1");

    fireEvent.click(await screen.findByRole("button", { name: "Generate AI Summary" }));

    expect(await screen.findByText(/Repeated torque defects may indicate/i)).toBeInTheDocument();
    expect(screen.getByText("Evidence")).toBeInTheDocument();
    expect(screen.getByText("Recommended Next Checks")).toBeInTheDocument();
    expect(screen.getByText("medium")).toBeInTheDocument();
    expect(screen.getByText("Limitations")).toBeInTheDocument();
  });

  it("renders an AI summary error state if generation fails", async () => {
    mockApiResponses({
      "POST /api/v1/investigations/1/ai-summary": new Error("summary failed"),
    });

    renderApp("/investigations/1");

    fireEvent.click(await screen.findByRole("button", { name: "Generate AI Summary" }));

    expect(await screen.findByText("Unable to generate AI summary.")).toBeInTheDocument();
  });

  it("displays an existing AI summary", async () => {
    mockApiResponses({
      "GET /api/v1/investigations/1": {
        ...mockExistingInvestigation(),
        ai_summary: {
          likely_issue: "Existing saved summary may indicate a station-specific torque issue.",
          affected_station: "ST-TORQUE",
          affected_equipment: "EQ-TQ-01",
          evidence: ["Existing summary evidence."],
          recommended_next_checks: ["Check torque calibration."],
          confidence: "low",
          limitations: ["Saved summary is based on prior platform evidence."],
        },
      },
    });

    renderApp("/investigations/1");

    expect(await screen.findByText(/Existing saved summary/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Regenerate AI Summary" })).toBeInTheDocument();
  });
});

function mockExistingInvestigation() {
  return {
    id: 1,
    alert_id: 1,
    title: "Investigate repeated torque defects",
    summary: "Initial review",
    root_cause_hypothesis: "Torque tool may be drifting out of calibration",
    evidence_json: { source: "test" },
    ai_summary: null,
    status: "draft",
    created_at: "2026-06-09T12:20:00Z",
    opened_at: "2026-06-09T12:20:00Z",
    updated_at: "2026-06-09T12:25:00Z",
    closed_at: null,
  };
}
