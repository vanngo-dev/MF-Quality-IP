import { describe, expect, it } from "vitest";

import { DEFAULT_API_BASE_URL, getApiBaseUrl } from "../services/apiClient";
import { updateAlertStatus } from "../services/alertsApi";
import { getHealth } from "../services/healthApi";
import { getStations } from "../services/stationsApi";
import { getVehicleByVin } from "../services/vehiclesApi";
import { mockApiResponses } from "./testUtils";

describe("apiClient", () => {
  it("uses the configured base URL or default base URL", () => {
    expect(getApiBaseUrl()).toBe(DEFAULT_API_BASE_URL);
  });

  it("builds correct URLs for health and read API calls", async () => {
    const fetchMock = mockApiResponses();

    await getHealth();
    await getStations();
    await getVehicleByVin("MQPLANT0000000001");

    expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:8000/health");
    expect(fetchMock.mock.calls[1][0]).toBe("http://localhost:8000/api/v1/stations");
    expect(fetchMock.mock.calls[2][0]).toBe("http://localhost:8000/api/v1/vehicles/MQPLANT0000000001");
  });

  it("builds the alert status mutation URL and payload", async () => {
    const fetchMock = mockApiResponses();

    await updateAlertStatus(1, "acknowledged");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/alerts/1/status",
      expect.objectContaining({
        body: JSON.stringify({ status: "acknowledged" }),
        method: "PATCH",
      }),
    );
  });
});
