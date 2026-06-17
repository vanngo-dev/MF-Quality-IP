import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AlertsPage } from "../features/alerts/AlertsPage";
import { DefectsPage } from "../features/defects/DefectsPage";
import { EquipmentPage } from "../features/equipment/EquipmentPage";
import { InvestigationsPage } from "../features/investigations/InvestigationsPage";
import { StationsPage } from "../features/stations/StationsPage";
import { VehiclesPage } from "../features/vehicles/VehiclesPage";
import { mockApiResponses, renderWithQueryClient } from "./testUtils";

describe("Phase 9 live data pages", () => {
  it("renders the stations table from mocked API data", async () => {
    mockApiResponses();

    renderWithQueryClient(<StationsPage />);

    expect(await screen.findByText("ST-TORQUE")).toBeInTheDocument();
    expect(screen.getByText("Torque Station")).toBeInTheDocument();
    expect(screen.getAllByText("Workstation")).toHaveLength(2);
  });

  it("renders the equipment table from mocked API data", async () => {
    mockApiResponses();

    renderWithQueryClient(<EquipmentPage />);

    expect(await screen.findByText("EQ-TQ-01")).toBeInTheDocument();
    expect(screen.getAllByText("Torque Tool")[0]).toBeInTheDocument();
    expect(screen.getByText("ST-TORQUE")).toBeInTheDocument();
    expect(screen.getAllByText("Active")[0]).toBeInTheDocument();
  });

  it("renders vehicles and fetches selected VIN details", async () => {
    mockApiResponses();

    renderWithQueryClient(<VehiclesPage />);

    expect(await screen.findByText("MQPLANT0000000001")).toBeInTheDocument();
    expect(screen.getByText("MQPLANT0000000002")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("VIN Search"), {
      target: { value: "MQPLANT0000000002" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Search VIN" }));

    const details = await screen.findByLabelText("Selected vehicle details");

    expect(within(details).getByText("MQPLANT0000000002")).toBeInTheDocument();
    expect(within(details).getByText("Station event history will be added in a later phase.")).toBeInTheDocument();
  });

  it("renders the defects table from mocked API data", async () => {
    mockApiResponses();

    renderWithQueryClient(<DefectsPage />);

    expect(await screen.findByText("TORQUE_LOW")).toBeInTheDocument();
    expect(screen.getByText("MQPLANT0000000001")).toBeInTheDocument();
    expect(screen.getByText("ST-TORQUE")).toBeInTheDocument();
    expect(screen.getByText("Torque value below threshold")).toBeInTheDocument();
  });

  it("filters defects by severity", async () => {
    mockApiResponses();

    renderWithQueryClient(<DefectsPage />);

    expect(await screen.findByText("TORQUE_LOW")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Severity"), { target: { value: "critical" } });

    expect(screen.getByText("PAINT_CHIP")).toBeInTheDocument();
    expect(screen.queryByText("TORQUE_LOW")).not.toBeInTheDocument();
  });

  it("filters defects by status", async () => {
    mockApiResponses();

    renderWithQueryClient(<DefectsPage />);

    expect(await screen.findByText("TORQUE_LOW")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Status"), { target: { value: "resolved" } });

    expect(screen.getByText("PAINT_CHIP")).toBeInTheDocument();
    expect(screen.queryByText("TORQUE_LOW")).not.toBeInTheDocument();
  });

  it("renders the alerts table from mocked API data", async () => {
    mockApiResponses();

    renderWithQueryClient(<AlertsPage />);

    expect(await screen.findByText("REPEATED_DEFECT_STATION")).toBeInTheDocument();
    expect(screen.getByText("Repeated torque defects")).toBeInTheDocument();
    expect(screen.getByText("Multiple torque defects detected at the station")).toBeInTheDocument();
  });

  it("filters alerts by severity", async () => {
    mockApiResponses();

    renderWithQueryClient(<AlertsPage />);

    expect(await screen.findByText("Repeated torque defects")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Severity"), { target: { value: "high" } });

    expect(screen.getByText("Low vision confidence")).toBeInTheDocument();
    expect(screen.queryByText("Repeated torque defects")).not.toBeInTheDocument();
  });

  it("filters alerts by status", async () => {
    mockApiResponses();

    renderWithQueryClient(<AlertsPage />);

    expect(await screen.findByText("Repeated torque defects")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Status"), { target: { value: "acknowledged" } });

    expect(screen.getByText("Low vision confidence")).toBeInTheDocument();
    expect(screen.queryByText("Repeated torque defects")).not.toBeInTheDocument();
  });

  it("acknowledges an open alert through the status mutation", async () => {
    const fetchMock = mockApiResponses();

    renderWithQueryClient(<AlertsPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Acknowledge" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/alerts/1/status",
        expect.objectContaining({
          body: JSON.stringify({ status: "acknowledged" }),
          method: "PATCH",
        }),
      );
    });
  });

  it("renders investigations from mocked API data", async () => {
    mockApiResponses();

    renderWithQueryClient(<InvestigationsPage />);

    expect(await screen.findByText("Investigate repeated torque defects")).toBeInTheDocument();
    expect(screen.getByText("Torque tool may be drifting out of calibration")).toBeInTheDocument();
    expect(screen.getByText("Draft")).toBeInTheDocument();
  });
});
