import { apiGet } from "./apiClient";

export type Vehicle = {
  id: number;
  vin: string;
  model: string;
  model_year: number;
  color: string;
  line_id: number;
  current_station_id: number | null;
  build_status: string;
};

export function listVehicles() {
  return apiGet<Vehicle[]>("/api/v1/vehicles");
}
