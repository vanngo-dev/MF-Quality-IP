import { apiGet } from "./apiClient";

export type SearchResult = {
  id: string;
  type: "defect" | "alert" | "investigation" | "event" | string;
  title: string;
  summary: string | null;
  score: number | null;
  source: Record<string, unknown>;
};

export type GroupedSearchResults = {
  defects: SearchResult[];
  alerts: SearchResult[];
  investigations: SearchResult[];
  events: SearchResult[];
};

export type GroupedSearchResponse = {
  query: string;
  results: GroupedSearchResults;
};

export type SearchCollectionResponse = {
  query: string;
  results: SearchResult[];
};

export function searchAll(query: string) {
  return apiGet<GroupedSearchResponse>(`/api/v1/search?q=${encodeURIComponent(query)}`);
}

export function searchDefects(query: string) {
  return apiGet<SearchCollectionResponse>(`/api/v1/search/defects?q=${encodeURIComponent(query)}`);
}

export function searchAlerts(query: string) {
  return apiGet<SearchCollectionResponse>(`/api/v1/search/alerts?q=${encodeURIComponent(query)}`);
}

export function searchInvestigations(query: string) {
  return apiGet<SearchCollectionResponse>(`/api/v1/search/investigations?q=${encodeURIComponent(query)}`);
}

export function searchEvents(query: string) {
  return apiGet<SearchCollectionResponse>(`/api/v1/search/events?q=${encodeURIComponent(query)}`);
}
