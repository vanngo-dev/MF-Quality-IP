import { apiGet, apiPatch } from "./apiClient";

export type Alert = {
  id: number;
  alert_code: string;
  station_id: number;
  equipment_id: number | null;
  severity: string;
  title: string;
  description: string;
  evidence_json: Record<string, unknown>;
  status: string;
  created_at: string;
};

export function listAlerts() {
  return apiGet<Alert[]>("/api/v1/alerts");
}

export function getAlertById(id: number) {
  return apiGet<Alert>(`/api/v1/alerts/${id}`);
}

export function updateAlertStatus(id: number, status: string) {
  return apiPatch<Alert, { status: string }>(`/api/v1/alerts/${id}/status`, { status });
}

export const getAlerts = listAlerts;
