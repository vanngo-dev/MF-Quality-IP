# Manufacturing Quality Intelligence Platform

Full-stack portfolio project for manufacturing quality workflows, event-driven ingestion, investigation summaries, and operational dashboards.

## Current Phase

Phase 11 adds the engineer quality investigation workflow on top of the Phase 1-10 platform:

- FastAPI backend with a health contract.
- React + TypeScript + Vite frontend dashboard connected to live API data with TanStack Query.
- PostgreSQL, Redpanda, and Elasticsearch local services through Docker Compose.
- SQLAlchemy ORM models for plants, production lines, stations, equipment, vehicles, events, readings, defects, alerts, and investigations.
- Alembic migration for the initial domain schema.
- Seed data for local demos and tests.
- Read-only `/api/v1` endpoints for the manufacturing domain.
- Defect, quality alert, and investigation REST APIs.
- Business validation for workflow severity, status, and foreign-key references.
- Python event generator for station, sensor reading, inspection, and defect events.
- Deterministic and random JSON event output for tests, demos, and future streaming.
- Kafka-compatible producer support for publishing generated events to Redpanda.
- Streaming topics for station events, sensor readings, defects, alerts, and investigations.
- Separate Python worker that consumes `station.events`, `sensor.readings`, and `quality.defects`.
- Idempotent event persistence into `production_events`, `sensor_readings`, and `defects`.
- Invalid event logging with a dead-letter placeholder.
- Rule-based alert engine for repeated defects, sensor threshold breaches, defect spikes, and inspection failures.
- Alert persistence into `quality_alerts`.
- Alert publishing to the `quality.alerts` Redpanda topic.
- React Router routes for dashboard, stations, equipment, vehicles, defects, alerts, and investigations.
- Reusable frontend layout and UI components.
- API client functions for health, stations, equipment, vehicles, defects, alerts, and investigations.
- Live dashboard metrics for vehicles, open defects, open alerts, critical alerts, and top defect station.
- Frontend tables for stations, equipment, vehicles, defects, alerts, and investigations populated from backend APIs.
- VIN search and selected vehicle details.
- Client-side defect and alert filters.
- Alert acknowledgement through `PATCH /api/v1/alerts/{id}/status`.
- Elasticsearch search indexes for defects, alerts, investigations, and event summaries.
- Backend search endpoints for grouped and specialized search results.
- Reindex command for rebuilding search documents from PostgreSQL.
- Frontend `/search` page with grouped results for defects, alerts, investigations, and events.
- Alert detail page for reviewing alert evidence and opening investigations.
- Investigation detail page for editing summaries, root-cause hypotheses, and statuses.
- Investigation workflow actions for acknowledging alerts, creating investigations, resolving investigations, and resolving related alerts.
- Backend and frontend automated tests.
- GitHub Actions CI for backend and frontend checks.
- Documentation and YouTube tutorial notes.

Detailed notes:

- `docs/phase-01-foundation.md`
- `docs/phase-02-postgres-domain-models.md`
- `docs/phase-03-quality-workflow-apis.md`
- `docs/phase-04-simulated-event-generator.md`
- `docs/phase-05-redpanda-event-streaming.md`
- `docs/phase6.md`
- `docs/phase7.md`
- `docs/phase8.md`
- `docs/phase9.md`
- `docs/phase10.md`
- `docs/phase11.md`
- `docs/architecture.md`
- `docs/event-contracts.md`
- `docs/data-model.md`
- `docs/api-contracts.md`
- `docs/testing-strategy.md`

## Repository Structure

```text
backend/              FastAPI application and backend tests
event-generator/      Standalone simulated manufacturing event generator
worker/               Kafka consumer worker for event persistence
frontend/             React, TypeScript, and Vite application
docs/                 Phase notes and tutorial notes
.github/workflows/    GitHub Actions CI
docker-compose.yml    Local platform services
```

The FastAPI backend lives in `backend/`. This project does not use an `api/` folder.

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop

## Backend

```powershell
python -m venv .venv
.\.venv\Scripts\activate
cd backend
pip install -e .
python -m uvicorn app.main:app --reload --port 8000
```

Backend API:

- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
- Plants: http://localhost:8000/api/v1/plants
- Lines: http://localhost:8000/api/v1/lines
- Stations: http://localhost:8000/api/v1/stations
- Equipment: http://localhost:8000/api/v1/equipment
- Vehicles: http://localhost:8000/api/v1/vehicles
- Defects: http://localhost:8000/api/v1/defects
- Alerts: http://localhost:8000/api/v1/alerts
- Investigations: http://localhost:8000/api/v1/investigations
- Search: http://localhost:8000/api/v1/search?q=torque

## Frontend

```powershell
cd frontend
npm install
npm run test
npm run dev
```

Frontend app:

- http://localhost:5173

Phase 10 uses live backend API data and search endpoints. Start the backend on port 8000 for the browser demo. Frontend tests mock API responses, so the backend does not need to be running for automated frontend tests.

## Local Services

```powershell
docker compose up -d postgres redpanda elasticsearch
```

Services:

- PostgreSQL: localhost:5432
- Redpanda broker: localhost:19092
- Redpanda Console: http://localhost:8080
- Elasticsearch: http://localhost:9200

## Database Setup

```powershell
docker compose up postgres
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

If editable install is not available in your environment, install the backend dependencies directly:

```powershell
pip install fastapi "uvicorn[standard]" pytest httpx pydantic-settings sqlalchemy alembic psycopg2-binary elasticsearch
```

The seed command creates:

- 1 plant
- 2 production lines
- 6 stations
- 8 equipment records
- 10 vehicles

## Tests

Backend:

```powershell
cd backend
pytest
```

Event generator:

```powershell
cd event-generator
pytest
```

Worker:

```powershell
cd worker
pytest
```

Frontend:

```powershell
cd frontend
npm run test
npm run build
```

Docker Compose syntax:

```powershell
docker compose config
```

## Manual Workflow Checks

```powershell
curl http://localhost:8000/api/v1/vehicles
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/defects
curl http://localhost:8000/api/v1/alerts
curl http://localhost:8000/api/v1/investigations
```

## Event Generator

The event generator can print valid JSON events or publish them to Redpanda topics.

```powershell
cd event-generator
pip install -e .
pytest
python -m app.main --mode deterministic
python -m app.main --mode random --count 10
python -m app.main --mode deterministic --publish --broker localhost:19092
python -m app.main --mode random --count 10 --publish --broker localhost:19092
```

If editable install is not available:

```powershell
pip install pydantic pytest
```

Optional file output:

```powershell
python -m app.main --mode deterministic --output events.jsonl
python -m app.main --mode random --count 100 --output events.jsonl
```

## Streaming

Start Redpanda and Redpanda Console:

```powershell
docker compose up redpanda redpanda-console
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Publish demo events:

```powershell
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

Makefile shortcuts are also available:

```powershell
make up-streaming
make create-topics
make produce-demo-events
make produce-random-events
make produce-defect-spike
```

On Windows systems without Make, use the direct PowerShell commands above.

## Worker Ingestion

The worker is separate from FastAPI. FastAPI serves API requests, while the worker consumes Redpanda messages and writes accepted events to PostgreSQL.

| Topic | Table |
| --- | --- |
| `station.events` | `production_events` |
| `sensor.readings` | `sensor_readings` |
| `quality.defects` | `defects` |

Run the full local ingestion flow:

```powershell
docker compose up postgres redpanda redpanda-console
```

In another terminal:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start the worker:

```powershell
cd worker
pip install -e .
python -m app.main
```

Publish deterministic demo events:

```powershell
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

Verify through the API and database:

```powershell
curl http://localhost:8000/api/v1/defects
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/vehicles
docker compose exec postgres psql -U quality -d quality
```

Useful SQL checks:

```sql
select count(*) from production_events;
select count(*) from sensor_readings;
select count(*) from defects;
```

The worker uses `KAFKA_BOOTSTRAP_SERVERS` and `DATABASE_URL`. The repo default database URL is:

```text
postgresql+psycopg2://quality:quality@localhost:5432/quality
```

Duplicate event IDs are skipped safely. Invalid events are logged and skipped. Phase 7 generates rule-based quality alerts after successful worker persistence.

## Rule-Based Alerts

Phase 7 runs deterministic quality rules inside the worker after events are persisted. Rules inspect persisted defects, sensor readings, and production events, then create `quality_alerts` records with evidence.

Implemented alert rules:

- `REPEATED_DEFECT_STATION`
- `EQUIPMENT_TEMPERATURE_HIGH`
- `TORQUE_OUT_OF_TOLERANCE`
- `VISION_CONFIDENCE_LOW`
- `DEFECT_CODE_SPIKE`
- `CONSECUTIVE_INSPECTION_FAILURES`

Produce a deterministic defect spike:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Verify alerts:

```powershell
curl http://localhost:8000/api/v1/alerts
docker compose exec redpanda rpk topic consume quality.alerts --num 5
```

Phase 10 adds Elasticsearch search for indexed quality records.

## Frontend Dashboard Data Integration

Phase 9 turns the frontend shell into a live internal dashboard. Pages call the FastAPI backend through `VITE_API_BASE_URL` and TanStack Query manages loading, error, success, refetch, and mutation states.

Routes:

- `/dashboard`
- `/search`
- `/stations`
- `/equipment`
- `/vehicles`
- `/defects`
- `/alerts`
- `/investigations`

The root route redirects to `/dashboard`.

The API base URL is configured with:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Connected pages:

- Dashboard live metrics and latest alerts
- Search grouped results
- Stations with defect and alert counts
- Equipment inventory
- Vehicles with VIN search and selected vehicle details
- Defects with severity and status filters
- Alerts with severity and status filters plus acknowledgement
- Investigations worklist

Sensor event detail history is not exposed by the backend API yet, so the dashboard shows `Not available yet` for latest sensor event timestamp and the vehicle page keeps the station event history placeholder. The full investigation detail workflow is intentionally not included until Phase 11.

## Elasticsearch Quality Search

Phase 10 indexes searchable documents into Elasticsearch:

| Index | Records |
| --- | --- |
| `manufacturing-defects` | defects |
| `manufacturing-alerts` | quality alerts |
| `manufacturing-investigations` | investigations |
| `manufacturing-events` | production event summaries |

The backend reads:

```text
ELASTICSEARCH_URL=http://localhost:9200
```

Rebuild search indexes from PostgreSQL:

```powershell
cd backend
python -m app.search.reindex
```

Makefile shortcut:

```powershell
make reindex-search
```

Search endpoints:

```text
GET /api/v1/search?q=torque
GET /api/v1/search/defects?q=torque
GET /api/v1/search/alerts?q=defect
GET /api/v1/search/investigations?q=root
GET /api/v1/search/events?q=station
```

Frontend route:

```text
http://localhost:5173/search
```

Advanced search filters are deferred. The full investigation lifecycle workflow starts in Phase 11, and AI summaries start in Phase 12.

## Quality Investigation Workflow

Phase 11 lets engineers move from an alert to an investigation:

```text
Alert detail -> evidence review -> create investigation -> edit hypothesis and notes -> resolve investigation -> resolve alert
```

Workflow endpoints:

```text
POST /api/v1/alerts/{id}/investigation
PATCH /api/v1/investigations/{id}
PATCH /api/v1/investigations/{id}/status
PATCH /api/v1/alerts/{id}/status
```

Frontend routes:

```text
/alerts/{id}
/investigations/{id}
```

Investigation statuses:

- `draft`
- `active`
- `waiting_on_data`
- `resolved`

Creating an investigation from an open or acknowledged alert moves the alert to `investigating`. Resolving an investigation also resolves the related alert. Evidence from the alert is copied into the investigation so the engineering context remains attached.

AI summary generation is intentionally not included yet. Phase 11 only displays the placeholder that AI summaries start in Phase 12.
