import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";

export const apiFixtures = {
  stations: [
    { id: 1, line_id: 1, code: "ST-TORQUE", name: "Torque Station", sequence_order: 1 },
    { id: 2, line_id: 1, code: "ST-PAINT", name: "Paint Inspection", sequence_order: 2 },
  ],
  equipment: [
    { id: 1, station_id: 1, asset_tag: "EQ-TQ-01", name: "Torque Tool", equipment_type: "Torque Tool" },
    { id: 2, station_id: 2, asset_tag: "EQ-VIS-01", name: "Vision Camera", equipment_type: "Camera" },
  ],
  vehicles: [
    {
      id: 1,
      vin: "MQPLANT0000000001",
      model: "Aster EV",
      model_year: 2026,
      color: "Silver",
      line_id: 1,
      current_station_id: 1,
      build_status: "in_progress",
    },
    {
      id: 2,
      vin: "MQPLANT0000000002",
      model: "Aster EV",
      model_year: 2026,
      color: "Blue",
      line_id: 1,
      current_station_id: 2,
      build_status: "complete",
    },
  ],
  defects: [
    {
      id: 1,
      defect_code: "TORQUE_LOW",
      vehicle_id: 1,
      station_id: 1,
      equipment_id: 1,
      severity: "high",
      description: "Torque value below threshold",
      status: "open",
      detected_at: "2026-06-09T12:00:00Z",
    },
    {
      id: 2,
      defect_code: "PAINT_CHIP",
      vehicle_id: 2,
      station_id: 2,
      equipment_id: 2,
      severity: "critical",
      description: "Paint chip detected",
      status: "resolved",
      detected_at: "2026-06-09T12:05:00Z",
    },
  ],
  alerts: [
    {
      id: 1,
      alert_code: "REPEATED_DEFECT_STATION",
      station_id: 1,
      equipment_id: 1,
      severity: "critical",
      title: "Repeated torque defects",
      description: "Multiple torque defects detected at the station",
      evidence_json: { defect_count: 3 },
      status: "open",
      created_at: "2026-06-09T12:10:00Z",
    },
    {
      id: 2,
      alert_code: "VISION_CONFIDENCE_LOW",
      station_id: 2,
      equipment_id: 2,
      severity: "high",
      title: "Low vision confidence",
      description: "Inspection confidence dropped below threshold",
      evidence_json: { confidence: 0.8 },
      status: "acknowledged",
      created_at: "2026-06-09T12:15:00Z",
    },
  ],
  investigations: [
    {
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
    },
  ],
  search: {
    query: "torque",
    results: {
      defects: [
        {
          id: "1",
          type: "defect",
          title: "TORQUE_LOW",
          summary: "Torque value below threshold",
          score: 3.5,
          source: {
            id: 1,
            vin: "MQPLANT0000000001",
            station_code: "ST-TORQUE",
            equipment_code: "EQ-TQ-01",
            status: "open",
          },
        },
      ],
      alerts: [
        {
          id: "2",
          type: "alert",
          title: "Repeated torque defects",
          summary: "Multiple torque defects detected at the station",
          score: 2.5,
          source: {
            id: 2,
            station_code: "ST-TORQUE",
            equipment_code: "EQ-TQ-01",
            status: "open",
          },
        },
      ],
      investigations: [
        {
          id: "3",
          type: "investigation",
          title: "Investigate repeated torque defects",
          summary: "Torque tool may be drifting out of calibration",
          score: 1.5,
          source: {
            id: 3,
            status: "draft",
          },
        },
      ],
      events: [
        {
          id: "4",
          type: "event",
          title: "station_exit",
          summary: "ST-TORQUE",
          score: 1,
          source: {
            id: 4,
            vin: "MQPLANT0000000001",
            station_code: "ST-TORQUE",
          },
        },
      ],
    },
  },
};

type ApiResponseMap = Record<string, unknown>;

export function createApiResponseMap(overrides: ApiResponseMap = {}): ApiResponseMap {
  return {
    "GET /health": { status: "ok", service: "manufacturing-quality-api", environment: "test", dependencies: {} },
    "GET /api/v1/stations": apiFixtures.stations,
    "GET /api/v1/equipment": apiFixtures.equipment,
    "GET /api/v1/vehicles": apiFixtures.vehicles,
    "GET /api/v1/vehicles/MQPLANT0000000001": apiFixtures.vehicles[0],
    "GET /api/v1/vehicles/MQPLANT0000000002": apiFixtures.vehicles[1],
    "GET /api/v1/defects": apiFixtures.defects,
    "GET /api/v1/alerts": apiFixtures.alerts,
    "GET /api/v1/alerts/1": apiFixtures.alerts[0],
    "GET /api/v1/alerts/2": apiFixtures.alerts[1],
    "PATCH /api/v1/alerts/1/status": { ...apiFixtures.alerts[0], status: "acknowledged" },
    "PATCH /api/v1/alerts/2/status": { ...apiFixtures.alerts[1], status: "resolved" },
    "POST /api/v1/alerts/1/investigation": {
      ...apiFixtures.investigations[0],
      id: 2,
      alert_id: 1,
      status: "active",
      title: "Investigate Repeated torque defects",
    },
    "GET /api/v1/investigations": apiFixtures.investigations,
    "GET /api/v1/investigations/1": apiFixtures.investigations[0],
    "GET /api/v1/investigations/2": {
      ...apiFixtures.investigations[0],
      id: 2,
      status: "active",
      title: "Investigate Repeated torque defects",
    },
    "PATCH /api/v1/investigations/1": {
      ...apiFixtures.investigations[0],
      summary: "Updated summary",
      root_cause_hypothesis: "Updated hypothesis",
      updated_at: "2026-06-09T12:30:00Z",
    },
    "PATCH /api/v1/investigations/1/status": {
      ...apiFixtures.investigations[0],
      status: "resolved",
      closed_at: "2026-06-09T12:35:00Z",
      updated_at: "2026-06-09T12:35:00Z",
    },
    "GET /api/v1/search": apiFixtures.search,
    "GET /api/v1/search/defects": { query: "torque", results: apiFixtures.search.results.defects },
    "GET /api/v1/search/alerts": { query: "torque", results: apiFixtures.search.results.alerts },
    "GET /api/v1/search/investigations": { query: "torque", results: apiFixtures.search.results.investigations },
    "GET /api/v1/search/events": { query: "torque", results: apiFixtures.search.results.events },
    ...overrides,
  };
}

export function mockApiResponses(overrides: ApiResponseMap = {}) {
  const responses = createApiResponseMap(overrides);
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const key = getRequestKey(input, init);
    const value = responses[key];

    if (value instanceof Error) {
      throw value;
    }

    if (!(key in responses)) {
      return jsonResponse({ detail: `No test response for ${key}` }, 404);
    }

    return jsonResponse(value, 200);
  });

  vi.stubGlobal("fetch", fetchMock);

  return fetchMock;
}

export function mockApiFailure(status = 500) {
  const fetchMock = vi.fn(async () => jsonResponse({ detail: "Test API failure" }, status));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

export function renderWithQueryClient(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return {
    queryClient,
    ...render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>{ui}</MemoryRouter>
      </QueryClientProvider>,
    ),
  };
}

function getRequestKey(input: RequestInfo | URL, init?: RequestInit) {
  const rawUrl = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
  const isRequest = typeof Request !== "undefined" && input instanceof Request;
  const requestMethod = isRequest ? input.method : undefined;
  const method = (init?.method ?? requestMethod ?? "GET").toUpperCase();
  const pathname = new URL(rawUrl, "http://localhost").pathname;

  return `${method} ${pathname}`;
}

function jsonResponse(value: unknown, status: number) {
  return new Response(JSON.stringify(value), {
    status,
    headers: {
      "Content-Type": "application/json",
    },
  });
}
