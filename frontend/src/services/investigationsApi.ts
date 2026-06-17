import { apiGet } from "./apiClient";

export type Investigation = {
  id: number;
  alert_id: number;
  title: string;
  summary: string | null;
  root_cause_hypothesis: string | null;
  evidence_json: Record<string, object>;
  status: string;
  opened_at: string;
  updated_at: string;
  closed_at: string | null;
};

export function listInvestigations() {
  return apiGet<Investigation[]>("/api/v1/investigations");
}
