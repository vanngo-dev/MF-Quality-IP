import { apiGet } from "./apiClient";

export type Defect = {
  id: number;
  defect_code: string;
  vehicle_id: number;
  station_id: number;
  equipment_id: number | null;
  severity: string;
  description: string;
  status: string;
  detected_at: string;
};

export function listDefects() {
  return apiGet<Defect[]>("/api/v1/defects");
}

export function getDefectById(id: number) {
  return apiGet<Defect>(`/api/v1/defects/${id}`);
}

export const getDefects = listDefects;
