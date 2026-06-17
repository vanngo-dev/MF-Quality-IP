import { apiGet } from "./apiClient";

export type Station = {
  id: number;
  line_id: number;
  code: string;
  name: string;
  sequence_order: number;
};

export function listStations() {
  return apiGet<Station[]>("/api/v1/stations");
}

export const getStations = listStations;
