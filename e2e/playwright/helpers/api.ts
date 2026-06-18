import { expect, type APIRequestContext } from "@playwright/test";

import { buildManufacturingAlertFixture } from "./test-data";

type Station = {
  id: number;
};

type Equipment = {
  id: number;
  station_id: number;
};

export type QualityAlert = {
  id: number;
  alert_code: string;
  station_id: number;
  equipment_id: number | null;
  title: string;
};

export async function expectBackendHealthy(request: APIRequestContext, apiUrl: string) {
  const response = await request.get(`${apiUrl}/health`);
  expect(response.ok()).toBeTruthy();
  await expect(response).toBeOK();
}

export async function createAlertFixture(request: APIRequestContext, apiUrl: string): Promise<QualityAlert> {
  const equipmentResponse = await request.get(`${apiUrl}/api/v1/equipment`);
  await expect(equipmentResponse).toBeOK();
  const equipment = (await equipmentResponse.json()) as Equipment[];

  const stationsResponse = await request.get(`${apiUrl}/api/v1/stations`);
  await expect(stationsResponse).toBeOK();
  const stations = (await stationsResponse.json()) as Station[];

  expect(stations.length, "Seeded stations are required for E2E alert fixtures.").toBeGreaterThan(0);
  const selectedEquipment = equipment[0] ?? null;
  const stationId = selectedEquipment?.station_id ?? stations[0].id;
  const payload = buildManufacturingAlertFixture({
    equipmentId: selectedEquipment?.id ?? null,
    stationId,
  });

  const response = await request.post(`${apiUrl}/api/v1/alerts`, { data: payload });
  await expect(response).toBeOK();

  return (await response.json()) as QualityAlert;
}
