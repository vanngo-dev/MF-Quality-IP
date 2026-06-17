import { apiGet, apiPatch, apiPost } from "./apiClient";

export type Investigation = {
  id: number;
  alert_id: number;
  title: string;
  summary: string | null;
  root_cause_hypothesis: string | null;
  evidence_json: Record<string, unknown>;
  status: string;
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

export function getInvestigationById(id: number) {
  return apiGet<Investigation>(`/api/v1/investigations/${id}`);
}

export function createInvestigation(payload: CreateInvestigationRequest) {
  return apiPost<Investigation, CreateInvestigationRequest>("/api/v1/investigations", payload);
}

export function updateInvestigation(id: number, payload: UpdateInvestigationRequest) {
  return apiPatch<Investigation, UpdateInvestigationRequest>(`/api/v1/investigations/${id}`, payload);
}

export const getInvestigations = listInvestigations;
