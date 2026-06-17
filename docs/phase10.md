# Phase 10 — Elasticsearch Quality Investigation Search

## Goal

Add Elasticsearch indexing and search for quality investigations, defects, alerts, and manufacturing event summaries.

This phase gives engineers a search workflow for VINs, stations, equipment, defect codes, alert titles, investigation text, root-cause hypotheses, and free-text descriptions.

Phase 10 does not add the full investigation lifecycle workflow or AI summaries. Those start in later phases.

## What Was Built

Phase 10 adds:

- Elasticsearch dependency metadata for the backend
- backend search package under `backend/app/search/`
- search document builders for defects, alerts, investigations, and event summaries
- index functions for `index_defect`, `index_alert`, `index_investigation`, and `index_event_summary`
- reindex command with `python -m app.search.reindex`
- Makefile shortcut with `make reindex-search`
- FastAPI search router under `/api/v1/search`
- grouped search endpoint
- specialized search endpoints for defects, alerts, investigations, and events
- frontend search API service
- frontend `/search` route
- sidebar Search link
- Search page with input, loading state, error state, grouped results, result type badges, result links, and no-results state
- backend tests with mocked Elasticsearch
- frontend tests with mocked API responses

## Why This Matters for Manufacturing Quality

Quality investigations often start with partial clues: a VIN, a station code, an equipment tag, a defect code, or a phrase from an alert. Those clues can exist across several tables.

PostgreSQL remains the system of record, but Elasticsearch is better suited for fast free-text search across denormalized documents. Phase 10 adds that searchable layer without changing the core relational model.

## Search Architecture

The Phase 10 search flow is:

```text
PostgreSQL records -> reindex command -> Elasticsearch indexes -> FastAPI search API -> React search page
```

The backend reads:

```text
ELASTICSEARCH_URL=http://localhost:9200
```

An index is a searchable collection of documents. A search document is a JSON object created from a database record and related lookup fields, such as VIN, station code, and equipment code.

## Indexes Added

Indexes:

| Index | Source records |
| --- | --- |
| `manufacturing-defects` | `defects` |
| `manufacturing-alerts` | `quality_alerts` |
| `manufacturing-investigations` | `investigations` |
| `manufacturing-events` | `production_events` |

## Documents Indexed

Defect documents include:

- `id`
- `defect_code`
- `vehicle_id`
- `vin`
- `station_id`
- `station_code`
- `equipment_id`
- `equipment_code`
- `severity`
- `status`
- `description`
- `detected_at`
- `created_at`
- `type = defect`

Alert documents include:

- `id`
- `alert_code`
- `station_id`
- `station_code`
- `equipment_id`
- `equipment_code`
- `severity`
- `status`
- `title`
- `description`
- `evidence_json`
- `created_at`
- `type = alert`

Investigation documents include:

- `id`
- `alert_id`
- `title`
- `summary`
- `root_cause_hypothesis`
- `ai_summary`
- `status`
- `created_at`
- `updated_at`
- `type = investigation`

`ai_summary` is set to `null` until Phase 12.

Event summary documents include:

- `id`
- `event_id`
- `event_type`
- `vehicle_id`
- `vin`
- `station_id`
- `station_code`
- `equipment_id`
- `equipment_code`
- `payload_json`
- `event_timestamp`
- `type = event`

## API Endpoints Added

Grouped search:

```text
GET /api/v1/search?q=torque
```

Response:

```json
{
  "query": "torque",
  "results": {
    "defects": [],
    "alerts": [],
    "investigations": [],
    "events": []
  }
}
```

Specialized endpoints:

```text
GET /api/v1/search/defects?q=torque
GET /api/v1/search/alerts?q=defect
GET /api/v1/search/investigations?q=root
GET /api/v1/search/events?q=station
```

Specialized response:

```json
{
  "query": "torque",
  "results": []
}
```

Empty search queries return `400`:

```json
{
  "detail": "Search query must not be empty."
}
```

## Frontend Search Page

The frontend adds:

```text
/search
```

The sidebar includes a Search link.

The Search page includes:

- search input
- submit button
- loading state
- error state
- grouped results
- result type badge
- basic result cards
- links to existing pages for defects, alerts, and investigations
- no-results message

The page does not add advanced filters. Those are intentionally deferred.

## Reindex Command

Run:

```powershell
cd backend
python -m app.search.reindex
```

The reindex command:

- connects to PostgreSQL
- reads defects
- reads alerts
- reads investigations
- reads production event summaries
- writes documents into Elasticsearch
- prints counts indexed
- handles empty tables gracefully

Makefile shortcut:

```powershell
make reindex-search
```

## How to Run It

Start services:

```powershell
docker compose up postgres elasticsearch
```

If Redpanda and worker are needed for demo data:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Run backend setup:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

If editable install is not supported:

```powershell
pip install fastapi "uvicorn[standard]" pytest httpx pydantic-settings sqlalchemy alembic psycopg2-binary elasticsearch
```

Optional: create demo data with prior phases:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Run reindex:

```powershell
cd backend
python -m app.search.reindex
```

Start API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Start frontend:

```powershell
cd frontend
npm install
npm run test
npm run dev
```

Open:

```text
http://localhost:5173/search
```

## Automated Tests

Backend:

```powershell
cd backend
pytest
```

Backend tests cover:

- empty query validation
- grouped response shape
- defects search endpoint
- alerts search endpoint
- investigations search endpoint
- no-results grouped response
- search service query building
- search service hit parsing
- missing index handling
- defect document building
- alert document building
- investigation document building
- event summary document building
- empty reindex behavior

Frontend:

```powershell
cd frontend
npm run test
```

Frontend tests cover:

- Search page render
- Search input text entry
- API call on submit
- loading state
- error state
- grouped result rendering
- no-results message
- sidebar Search link

Normal automated tests use mocked Elasticsearch and mocked frontend API responses.

## Manual Tests

1. Start PostgreSQL and Elasticsearch.
2. Run backend migrations.
3. Seed the database.
4. Create demo defects, alerts, investigations, or events if needed.
5. Run `python -m app.search.reindex`.
6. Start the backend API.
7. Call `curl "http://localhost:8000/api/v1/search?q=torque"`.
8. Call `curl "http://localhost:8000/api/v1/search/defects?q=torque"`.
9. Call `curl "http://localhost:8000/api/v1/search/alerts?q=defect"`.
10. Call `curl "http://localhost:8000/api/v1/search/investigations?q=root"`.
11. Start the frontend.
12. Open `http://localhost:5173/search`.
13. Search for `torque`.
14. Confirm grouped results render if indexed data exists.
15. Search for a nonsense query.
16. Confirm the no-results message appears.
17. Stop the backend or Elasticsearch.
18. Confirm the error state appears.

## Expected Results

- Elasticsearch starts locally on port 9200.
- Reindex command runs.
- Reindex command prints counts for defects, alerts, investigations, and events.
- Search endpoints return grouped results.
- Specialized search endpoints return one result group.
- Frontend `/search` page exists.
- Sidebar includes Search.
- Search page displays grouped results.
- Tests pass in a normal local environment.
- No Phase 11 investigation lifecycle workflow is added.
- No Phase 12 AI summary logic is added.

## Common Errors and Fixes

### Elasticsearch container not running

Start Elasticsearch:

```powershell
docker compose up postgres elasticsearch
```

### Wrong ELASTICSEARCH_URL

Set:

```text
ELASTICSEARCH_URL=http://localhost:9200
```

### Elasticsearch security enabled accidentally

Local Docker Compose should include:

```text
xpack.security.enabled=false
```

### Index does not exist

Run:

```powershell
cd backend
python -m app.search.reindex
```

### No search results because reindex was not run

Run the reindex command after creating or ingesting demo data.

### No search results because database has no demo defects or alerts

Seed the database and run the event generator or create workflow records through existing APIs.

### Backend CORS issue from frontend search page

Confirm:

```text
FRONTEND_ORIGIN=http://localhost:5173
```

### Frontend search error because backend is not running

Start the backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Search endpoint returns 400 for empty query

Submit a non-empty query.

## Git Commit

```bash
git add .
git commit -m "phase-10 elasticsearch quality investigation search"
```
