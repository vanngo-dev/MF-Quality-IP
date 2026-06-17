import { apiGet } from "./apiClient";

export type HealthResponse = {
  status: "ok";
  service: string;
  environment: string;
  dependencies: Record<string, string>;
};

export function getHealth() {
  return apiGet<HealthResponse>("/health");
}
