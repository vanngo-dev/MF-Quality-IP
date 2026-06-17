import { apiGet } from "./apiClient";

export type Alert = {
  id: number;
  alert_code: string;
  station_id: number;
  equipment_id: number | null;
  severity: string;
  title: string;
  description: string;
  evidence_json: Record<string, object>;
  status: string;
  created_at: string;
};

export function listAlerts() {
  return apiGet<Alert[]>("/api/v1/alerts");
}
