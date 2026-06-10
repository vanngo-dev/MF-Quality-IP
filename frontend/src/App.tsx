import { Activity, Database, RefreshCw, Search, Server } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import "./styles.css";

type HealthStatus = {
  status: "ok";
  service: string;
  environment: string;
  dependencies: Record<string, string>;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const dependencyLabels: Record<string, string> = {
  postgres: "PostgreSQL",
  redpanda: "Redpanda",
  elasticsearch: "Elasticsearch",
  ai_provider: "AI Provider",
};

const dependencyOrder = ["postgres", "redpanda", "elasticsearch", "ai_provider"];

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadHealth = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/health`);

      if (!response.ok) {
        throw new Error(`Health check failed with ${response.status}`);
      }

      setHealth((await response.json()) as HealthStatus);
    } catch {
      setHealth(null);
      setError("Backend health endpoint is not responding.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadHealth();
  }, [loadHealth]);

  const statusLabel = useMemo(() => {
    if (isLoading) {
      return "Checking";
    }

    return health?.status === "ok" ? "Operational" : "Unavailable";
  }, [health?.status, isLoading]);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Manufacturing Quality Intelligence</p>
          <h1>Quality Operations</h1>
        </div>
        <button className="icon-button" type="button" onClick={loadHealth} aria-label="Refresh API status">
          <RefreshCw aria-hidden="true" size={18} />
          <span>Refresh</span>
        </button>
      </header>

      <main>
        <section className="overview" aria-labelledby="foundation-status">
          <div className="section-heading">
            <Activity aria-hidden="true" size={22} />
            <div>
              <p className="eyebrow">Phase 1</p>
              <h2 id="foundation-status">Foundation Status</h2>
            </div>
          </div>

          <div className="overview-grid">
            <article className={`status-card ${health?.status === "ok" ? "is-ok" : "is-warning"}`}>
              <span className="metric-label">API Health</span>
              <strong>{statusLabel}</strong>
              <span className="metric-detail">{error ?? health?.service ?? "Waiting for backend response"}</span>
            </article>

            <article className="status-card">
              <span className="metric-label">Environment</span>
              <strong>{health?.environment ?? "local"}</strong>
              <span className="metric-detail">FastAPI on port 8000</span>
            </article>
          </div>
        </section>

        <section className="dependencies" aria-labelledby="service-status">
          <div className="section-heading">
            <Server aria-hidden="true" size={22} />
            <div>
              <p className="eyebrow">Local Stack</p>
              <h2 id="service-status">Service Contracts</h2>
            </div>
          </div>

          <div className="dependency-grid">
            {dependencyOrder.map((key) => {
              const Icon = key === "elasticsearch" ? Search : Database;
              const value = health?.dependencies[key] ?? "pending";

              return (
                <article className="dependency-card" key={key}>
                  <Icon aria-hidden="true" size={20} />
                  <div>
                    <span>{dependencyLabels[key]}</span>
                    <strong>{value}</strong>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
