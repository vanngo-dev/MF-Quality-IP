# Architecture

## Current Shape

The project is being built one phase at a time.

```text
frontend/          React + TypeScript user interface
backend/           FastAPI REST API and PostgreSQL domain model
event-generator/   Standalone Python event simulator
worker/            Standalone Python Kafka consumer and database ingestion worker
docker-compose.yml Local PostgreSQL, Redpanda, and Elasticsearch services
```

## Phase 4 Event Generator

The event generator simulates manufacturing data without depending on the backend, PostgreSQL, Redpanda, or Elasticsearch.

It generates:

- Station lifecycle events.
- Equipment sensor readings.
- Inspection events.
- Defect events.

## Why Simulated Data Is Useful

Simulated data lets the project demonstrate realistic manufacturing behavior before real shop-floor integrations exist. It also supports repeatable tests, demos, and future streaming work.

## Deterministic and Random Modes

Deterministic mode produces a fixed event sequence. Use it for tests and recorded demos.

Random mode produces a requested number of realistic events. Use it to show variety during local development.

## Phase 5 Redpanda Streaming

Redpanda provides a Kafka-compatible event streaming layer for local development.

Kafka-style streaming fits manufacturing systems because shop-floor activity is naturally event-driven: vehicles enter stations, tools report readings, inspections finish, and defects are detected over time.

The Phase 5 event generator publishes to these topics:

- `station.events`
- `sensor.readings`
- `quality.defects`

It also creates these future workflow topics:

- `quality.alerts`
- `investigation.events`

## Producer and Consumer Separation

The event generator is the producer. It sends events to Redpanda.

The worker consumer is intentionally separate from the FastAPI application. FastAPI handles request/response APIs. The worker handles long-running topic consumption and persistence so API latency, consumer retries, and streaming failures do not get tangled together.

## Phase 4 Boundary

Phase 4 validates event shape and event generation only. Kafka publishing is intentionally delayed until Phase 5 so the event contract can be tested before streaming infrastructure is added.

## How Phase 4 Prepared Streaming

The generator emits JSON Lines-compatible events with UUIDs and ISO timestamps. Phase 5 reuses these event contracts and adds a Redpanda/Kafka producer without changing the core payload design.

## Phase 5 Boundary

Phase 5 publishes events but does not save them to PostgreSQL. That keeps the streaming contract clear before Phase 6 adds worker consumption and persistence.

## Phase 6 Worker Consumers

Phase 6 adds a Python worker in `worker/`. It subscribes to the three producer topics from Phase 5:

- `station.events`
- `sensor.readings`
- `quality.defects`

The worker validates each event envelope, maps the payload to persistence data, resolves the referenced vehicle, station, and equipment rows, and writes to PostgreSQL.

See `docs/phase6.md` for the Phase 6 worker runbook and troubleshooting guide.

## Topic to Table Mapping

| Topic | Persisted table |
| --- | --- |
| `station.events` | `production_events` |
| `sensor.readings` | `sensor_readings` |
| `quality.defects` | `defects` |

The worker stores `event_id` on persisted event rows and checks that ID before inserting. This makes ingestion idempotent: if Redpanda redelivers an event or the generator publishes the same deterministic event twice, the worker logs a duplicate skip instead of creating another row.

Invalid events are logged through a dead-letter placeholder. Phase 6 does not build a full dead-letter replay workflow; it only prevents malformed or unresolvable messages from crashing the worker.

## Phase 6 Boundary

Phase 6 persists production events, sensor readings, and defects. It does not generate `quality_alerts`, run rule-based alert logic, add frontend screens, add Elasticsearch indexing, or create AI summaries. Alert rules start in Phase 7.

## Phase 7 Rule-Based Alert Engine

Phase 7 adds deterministic quality intelligence inside the worker. After the worker persists a new defect, sensor reading, or production event, it runs a rule engine against persisted data and creates `quality_alerts` records when thresholds are met.

The Phase 7 flow is:

```text
event-generator -> Redpanda topics -> worker consumers -> PostgreSQL events -> rule engine -> quality_alerts -> quality.alerts topic -> FastAPI read endpoints
```

Rules are deterministic and evidence-based. They cover repeated defects at the same station, high equipment temperature, torque readings outside tolerance, low vision confidence, defect-code spikes, and consecutive inspection failures.

Duplicate open alerts are prevented by checking for an existing open alert with the same `alert_code`, `station_id`, and `equipment_id`. Alert payloads are also published to `quality.alerts` when an alert is created.

See `docs/phase7.md` for the Phase 7 runbook and troubleshooting guide.

## Phase 7 Boundary

Phase 7 does not add frontend dashboard work, Elasticsearch indexing, AI summaries, or machine learning. Frontend dashboard work starts in Phase 8.

## Phase 8 React Frontend Foundation

Phase 8 turns the existing Vite frontend into a routed React + TypeScript dashboard shell.

The frontend is intentionally separate from the FastAPI backend:

```text
frontend React app -> API client foundation -> FastAPI backend routes
```

This separation keeps UI routing, layout, browser state, and component tests independent from backend service availability. Phase 8 pages use mock/static data so the frontend can run and test without PostgreSQL, Redpanda, or FastAPI running.

React Router provides internal routes for dashboard, stations, equipment, vehicles, defects, alerts, and investigations. Reusable components keep page headers, stat cards, tables, status badges, severity badges, loading states, and error states consistent across the application.

TanStack Query is configured as the server-state foundation for Phase 9, when the mock page data is replaced with live backend API responses.

See `docs/phase8.md` for the Phase 8 runbook and troubleshooting guide.

## Phase 8 Boundary

Phase 8 does not integrate live backend data, add Elasticsearch UI, add AI summaries, or add end-to-end browser tests. Live backend data integration is handled in Phase 9.

## Phase 9 Dashboard Data Integration

Phase 9 connects the existing React routes to the FastAPI backend:

```text
frontend pages -> TanStack Query hooks -> API service functions -> FastAPI backend -> PostgreSQL
```

The frontend uses `VITE_API_BASE_URL` to choose the backend origin. For local development the value is:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Each page owns its server-state queries and uses the shared loading and error components from Phase 8. Dashboard metrics are calculated client-side from the backend lists: total vehicles, open defects, open alerts, critical alerts, and the station with the most defects. The latest sensor event timestamp is shown as `Not available yet` because a sensor event detail API is not exposed yet.

The alert queue uses a TanStack Query mutation for:

```text
PATCH /api/v1/alerts/{id}/status
```

After an alert is acknowledged, the alerts query is invalidated so the table refetches from the backend.

Investigations remain a worklist table in Phase 9. The full investigation detail workflow is intentionally deferred until Phase 11.

## Phase 9 Boundary

Phase 9 connects dashboard pages to live backend data. It does not add Elasticsearch search, search UI, AI summaries, or the full investigation detail workflow. Elasticsearch search starts in Phase 10.

## Phase 10 Elasticsearch Quality Search

Phase 10 adds Elasticsearch as a search index for quality records. PostgreSQL remains the system of record. Elasticsearch stores denormalized search documents that are optimized for finding records by VIN, station, equipment, defect code, alert text, investigation text, and event summary data.

The search flow is:

```text
PostgreSQL records -> reindex command -> Elasticsearch indexes -> FastAPI search API -> React search page
```

Indexes:

- `manufacturing-defects`
- `manufacturing-alerts`
- `manufacturing-investigations`
- `manufacturing-events`

The backend uses:

```text
ELASTICSEARCH_URL=http://localhost:9200
```

The reindex command reads defects, alerts, investigations, and production events from PostgreSQL, builds search documents, and writes them to Elasticsearch:

```powershell
cd backend
python -m app.search.reindex
```

The search API returns grouped results from:

```text
GET /api/v1/search?q=torque
```

Specialized endpoints return one result group:

```text
GET /api/v1/search/defects?q=torque
GET /api/v1/search/alerts?q=defect
GET /api/v1/search/investigations?q=root
GET /api/v1/search/events?q=station
```

The frontend adds `/search` and a sidebar Search link. The page submits a free-text query, shows loading and error states, and renders grouped results for defects, alerts, investigations, and events.

## Phase 10 Boundary

Phase 10 adds basic indexing, reindexing, backend search APIs, and a frontend search page. It does not add advanced filters, full investigation lifecycle screens, or AI summaries. The full investigation workflow starts in Phase 11, and AI summaries start in Phase 12.

## Phase 11 Quality Investigation Workflow

Phase 11 adds the engineer workflow that connects alerts to investigations:

```text
quality alert -> alert detail -> create investigation -> edit notes and hypothesis -> update status -> resolve investigation and alert
```

Backend workflow endpoints:

```text
POST /api/v1/alerts/{id}/investigation
PATCH /api/v1/investigations/{id}
PATCH /api/v1/investigations/{id}/status
PATCH /api/v1/alerts/{id}/status
```

Creating an investigation from an alert copies `alert.evidence_json` into the investigation. This preserves the rule evidence that caused the alert, such as defect counts, time windows, station codes, equipment codes, and threshold values.

The backend prevents duplicate active investigations for the same alert. If an active investigation already exists, the create-from-alert endpoint returns `409`.

When an investigation is resolved, the backend sets `closed_at` and updates the related alert status to `resolved`. The existing alert status endpoint still allows engineers to acknowledge, investigate, or resolve alerts directly.

The frontend adds:

- `/alerts/:id`
- `/investigations/:id`
- `AlertDetailPage`
- `InvestigationDetailPage`
- `InvestigationForm`
- `EvidencePanel`
- `TimelinePanel`
- status action panels

Search result cards for alerts and investigations now route to the corresponding detail pages when possible.

## Phase 11 Boundary

Phase 11 adds the manual engineering workflow only. It does not call an AI provider, generate AI summaries, add AI summary buttons, or introduce Phase 12 endpoints.

## Phase 12 AI-Assisted Investigation Summary

Phase 12 adds evidence-grounded summary generation for investigations:

```text
investigation detail -> generate summary mutation -> backend evidence gathering -> summary provider -> saved ai_summary JSON -> frontend summary panel
```

The default provider is:

```text
AI_SUMMARY_PROVIDER=mock
```

The mock provider is deterministic and local. It inspects available platform evidence and produces a structured summary without external API keys or network calls.

Evidence sources:

- linked alert details
- alert `evidence_json`
- related defects at the alert station or equipment
- related sensor readings at the alert station or equipment
- related station events
- investigation title
- investigation summary notes
- investigation root-cause hypothesis
- investigation `evidence_json`

The summary response includes:

- likely issue
- affected station
- affected equipment
- evidence list
- recommended next checks
- confidence
- limitations

The backend persists the generated JSON into `investigations.ai_summary` and updates `updated_at`.

## Phase 12 Guardrails

AI summary generation must only use available evidence. It must not invent root cause or claim certainty. Missing evidence should be called out in limitations. Recommendations should be investigative checks, not production shutdown instructions unless existing platform evidence clearly supports that conclusion.

The OpenAI-compatible provider is a placeholder for future work. The app works without OpenAI-compatible settings, and normal tests do not make network calls.

## Phase 12 Boundary

Phase 12 adds the AI-assisted summary endpoint and UI panel only. It does not add Phase 13 end-to-end tests, chat UI, streaming output, or external model selection UI.

## Phase 13 End-to-End Workflow Tests

Phase 13 adds Playwright tests that exercise the running backend and frontend together:

```text
Playwright -> React frontend -> FastAPI backend -> PostgreSQL
```

The automated E2E suite creates alert fixtures through the FastAPI API, then drives the browser through dashboard loading, alert detail, investigation creation, AI summary generation, and investigation resolution. Redpanda and the worker remain part of the manual full-system demo, but automated E2E fixtures use the API so tests are not fragile around stream timing.

## Phase 14 Docker Compose Demo Architecture

Phase 14 makes the full local platform runnable through Docker Compose and Makefile commands.

Services:

- `postgres`: system-of-record database for plants, stations, equipment, vehicles, events, defects, alerts, and investigations.
- `redpanda`: Kafka-compatible broker for manufacturing event topics.
- `redpanda-console`: browser UI for inspecting Redpanda topics at `http://localhost:8080`.
- `elasticsearch`: local search index at `http://localhost:9200`.
- `backend`: FastAPI service at `http://localhost:8000`.
- `worker`: long-running Kafka consumer that persists events and generates rule-based alerts.
- `event-generator`: one-shot demo producer used by Makefile commands.
- `frontend`: Vite React app at `http://localhost:5173`.

Host URLs and Docker service URLs are intentionally different:

```text
Host machine:
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/manufacturing_quality
KAFKA_BOOTSTRAP_SERVERS=localhost:19092
ELASTICSEARCH_URL=http://localhost:9200

Inside Docker:
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/manufacturing_quality
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
ELASTICSEARCH_URL=http://elasticsearch:9200
```

The one-command demo flow is:

```text
make demo
  -> start infrastructure
  -> run Alembic migrations
  -> seed PostgreSQL
  -> create Redpanda topics
  -> publish defect-spike demo events
  -> start backend, worker, and frontend
```

The frontend connects to the backend with `VITE_API_BASE_URL=http://localhost:8000` because the browser runs on the host machine even when the frontend dev server is inside Docker. The backend connects to PostgreSQL through `postgres:5432` inside Docker, and the worker connects to Redpanda through `redpanda:9092`.

Elasticsearch remains a derived search index. PostgreSQL is still the source of truth, and `make reindex-search` runs the backend reindex command when demo data needs to be refreshed for the Search page.

Phase 14 does not add GitHub Actions CI. CI starts in Phase 15.
