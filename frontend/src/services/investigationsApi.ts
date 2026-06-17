import { apiGet, apiPatch, apiPost } from "./apiClient";

export type Investigation = {
  id: number;
  alert_id: number;
  title: string;
  summary: string | null;
  root_cause_hypothesis: string | null;
  evidence_json: Record<string, unknown>;
  ai_summary: string | null;
  status: string;
  created_at: string;
  opened_at: string;
  updated_at: string;
  closed_at: string | null;
};

export function listInvestigations() {
  return apiGet<Investigation[]>("/api/v1/investigations");
}

export type CreateInvestigationRequest = {
  alert_id: number;
  title: string;
  summary?: string | null;
  root_cause_hypothesis?: string | null;
  evidence_json?: Record<string, unknown>;
  status?: string;
};

export type UpdateInvestigationRequest = Partial<{
  title: string;
  summary: string | null;
  root_cause_hypothesis: string | null;
  evidence_json: Record<string, unknown>;
  status: string;
}>;

export type CreateInvestigationFromAlertRequest = {
  title: string;
  summary?: string | null;
  root_cause_hypothesis?: string | null;
  status?: string;
};

export function getInvestigationById(id: number) {
  return apiGet<Investigation>(`/api/v1/investigations/${id}`);
}

export function createInvestigation(payload: CreateInvestigationRequest) {
  return apiPost<Investigation, CreateInvestigationRequest>("/api/v1/investigations", payload);
}

export function updateInvestigation(id: number, payload: UpdateInvestigationRequest) {
  return apiPatch<Investigation, UpdateInvestigationRequest>(`/api/v1/investigations/${id}`, payload);
}

export function updateInvestigationStatus(id: number, status: string) {
  return apiPatch<Investigation, { status: string }>(`/api/v1/investigations/${id}/status`, { status });
}

export function createInvestigationFromAlert(alertId: number, payload: CreateInvestigationFromAlertRequest) {
  return apiPost<Investigation, CreateInvestigationFromAlertRequest>(
    `/api/v1/alerts/${alertId}/investigation`,
    payload,
  );
}

export const getInvestigations = listInvestigations;
