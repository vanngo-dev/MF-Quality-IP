import { useQuery } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../../components/layout/PageHeader";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { searchAll, type GroupedSearchResults, type SearchResult } from "../../services/searchApi";

const resultGroups: Array<{
  key: keyof GroupedSearchResults;
  title: string;
  linkTo?: string;
}> = [
  { key: "defects", title: "Defects", linkTo: "/defects" },
  { key: "alerts", title: "Alerts", linkTo: "/alerts" },
  { key: "investigations", title: "Investigations", linkTo: "/investigations" },
  { key: "events", title: "Events" },
];

export function SearchPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const trimmedQuery = submittedQuery.trim();
  const searchQuery = useQuery({
    queryKey: ["search", trimmedQuery],
    queryFn: () => searchAll(trimmedQuery),
    enabled: trimmedQuery.length > 0,
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmittedQuery(query.trim());
  }

  const hasResults = searchQuery.data ? countResults(searchQuery.data.results) > 0 : false;

  return (
    <section className="page-stack">
      <PageHeader title="Search" description="Search indexed quality records across defects, alerts, investigations, and events." />

      <form className="search-form" onSubmit={handleSubmit}>
        <label>
          Query
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="torque, VIN, station, defect code"
          />
        </label>
        <button className="secondary-button" type="submit">
          Search
        </button>
      </form>

      {searchQuery.isLoading ? <LoadingState message="Searching quality records..." /> : null}
      {searchQuery.isError ? <ErrorState message="Unable to search quality records." /> : null}

      {searchQuery.data ? (
        hasResults ? (
          <div className="search-results">
            {resultGroups.map((group) => (
              <ResultSection
                key={group.key}
                linkTo={group.linkTo}
                results={searchQuery.data.results[group.key]}
                title={group.title}
              />
            ))}
          </div>
        ) : (
          <p className="empty-results">No results found.</p>
        )
      ) : null}
    </section>
  );
}

function ResultSection({
  linkTo,
  results,
  title,
}: {
  linkTo?: string;
  results: SearchResult[];
  title: string;
}) {
  return (
    <section className="result-section" aria-label={`${title} search results`}>
      <div className="result-section-header">
        <h2>{title}</h2>
        <span>{results.length}</span>
      </div>

      {results.length > 0 ? (
        <div className="result-list">
          {results.map((result) => (
            <article className="result-card" key={`${result.type}-${result.id}`}>
              <div className="result-card-header">
                <span className={`type-badge type-${result.type}`}>{result.type}</span>
                <strong>{result.title}</strong>
              </div>
              {result.summary ? <p>{result.summary}</p> : null}
              <dl className="result-meta">
                {metadataItems(result).map((item) => (
                  <div key={item.label}>
                    <dt>{item.label}</dt>
                    <dd>{item.value}</dd>
                  </div>
                ))}
              </dl>
              {linkTo ? (
                <Link className="text-link" to={linkTo}>
                  Open {title}
                </Link>
              ) : null}
            </article>
          ))}
        </div>
      ) : (
        <p className="empty-results">No {title.toLowerCase()} found.</p>
      )}
    </section>
  );
}

function metadataItems(result: SearchResult) {
  return [
    { label: "ID", value: result.id },
    { label: "VIN", value: sourceValue(result, "vin") },
    { label: "Station", value: sourceValue(result, "station_code") ?? sourceValue(result, "station_id") },
    { label: "Equipment", value: sourceValue(result, "equipment_code") ?? sourceValue(result, "equipment_id") },
    { label: "Status", value: sourceValue(result, "status") },
  ].filter((item): item is { label: string; value: string } => item.value !== null);
}

function sourceValue(result: SearchResult, key: string) {
  const value = result.source[key];

  return value === null || value === undefined ? null : String(value);
}

function countResults(results: GroupedSearchResults) {
  return resultGroups.reduce((count, group) => count + results[group.key].length, 0);
}

