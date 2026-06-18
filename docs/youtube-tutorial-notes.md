# YouTube Tutorial Notes

## Phase 1: Project Foundation and Health Checks

### Episode Goal

Build the first commit of a manufacturing quality intelligence platform that can boot locally, expose a backend health contract, render a frontend operational status screen, and run automated tests.

### Recording Outline

1. Introduce the platform idea: manufacturing defects, investigations, event ingestion, search, and AI summaries.
2. Show the empty repository and explain the phase-by-phase rule.
3. Create the FastAPI backend and `/health` endpoint.
4. Create the React + TypeScript + Vite frontend.
5. Connect the frontend to the backend health endpoint.
6. Add Docker Compose services for PostgreSQL, Redpanda, and Elasticsearch.
7. Add backend and frontend tests.
8. Add GitHub Actions CI.
9. Run the automated checks.
10. Commit Phase 1.

### Concepts to Explain

- A health endpoint is a simple contract that tells other tools whether the API is reachable.
- Docker Compose gives the project repeatable local infrastructure.
- Alembic migrations will track database schema changes in later phases.
- React Testing Library verifies what a user sees instead of testing implementation details.
- CI protects the portfolio project by running tests on every pull request.

### Demo Script

```bash
cd backend
../.venv/Scripts/python -m uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```

Open:

- http://localhost:8000/health
- http://localhost:5173

### Commit Message

```bash
git commit -m "Initialize project foundation and health checks"
```

## Phase 2: PostgreSQL Database and Domain Models

### Episode Goal

Add the first real manufacturing data model: PostgreSQL storage, SQLAlchemy ORM classes, Alembic migration, deterministic seed data, and read-only domain API endpoints.

### What PostgreSQL Is Used For

PostgreSQL is the system of record for structured manufacturing quality data. In this project it stores plants, lines, stations, equipment, vehicles, production events, sensor readings, defects, alerts, and investigations.

### Why These Manufacturing Entities Matter

- Plants describe the manufacturing site.
- Production lines describe where products flow through the plant.
- Stations describe each ordered build or inspection step.
- Equipment identifies the tools, robots, cameras, scanners, and testers that generate quality signals.
- Vehicles give every defect, event, and investigation a product context.

### SQLAlchemy Concept

SQLAlchemy maps Python classes to database tables. A `Vehicle` class becomes the `vehicles` table, and each class attribute becomes a database column such as `vin`, `model`, or `build_status`.

### Alembic Concept

Alembic manages database schema changes. Instead of manually creating tables, the project keeps a migration file that can build the same schema every time with `alembic upgrade head`.

### Seed Data Concept

Seed data gives demos and tests a known starting point. Phase 2 creates 1 plant, 2 lines, 6 stations, 8 equipment records, and 10 vehicles so API responses are predictable.

### Manual Phase 2 Test Script

```powershell
docker compose up postgres
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
pytest
python -m uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
curl http://localhost:8000/api/v1/plants
curl http://localhost:8000/api/v1/lines
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/equipment
curl http://localhost:8000/api/v1/vehicles
```

### Phase 2 Commit Message

```bash
git commit -m "phase-2 postgres domain models migrations and seed data"
```

## Phase 3: Defect, Alert, and Investigation APIs

### Video Title:

Build Manufacturing Quality Workflow APIs with FastAPI and SQLAlchemy

### Goal of This Phase:

Create REST APIs that let quality teams record defects, raise alerts, and track engineering investigations.

### What We Build:

- Defect endpoints for create, list, and detail.
- Alert endpoints for create, list, detail, and status update.
- Investigation endpoints for create, list, detail, and update.
- Typed Pydantic schemas for every request and response.
- Tests for successful workflows and validation failures.

### Why This Matters for Manufacturing Quality:

Defects capture what went wrong on a vehicle. Alerts identify patterns that need attention. Investigations give engineers a place to track evidence, hypotheses, and root-cause progress.

### Code Walkthrough:

1. Review the existing `backend/` FastAPI structure.
2. Update SQLAlchemy workflow models.
3. Add the Alembic migration for workflow table changes.
4. Add Pydantic request and response schemas.
5. Add `defects.py`, `alerts.py`, and `investigations.py` routers.
6. Wire the routers into `app.main`.

### Testing Walkthrough:

Run:

```powershell
cd backend
pytest
```

Explain how tests reuse seeded vehicles and stations, then validate success cases, `404` invalid references, and `422` invalid enum values.

### Manual Demo:

```powershell
docker compose up postgres
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
pytest
python -m uvicorn app.main:app --reload --port 8000
```

Second terminal:

```powershell
curl http://localhost:8000/api/v1/vehicles
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/defects
curl http://localhost:8000/api/v1/alerts
curl http://localhost:8000/api/v1/investigations
```

### Common Errors:

- `404 Vehicle not found`: use a real vehicle ID from `/api/v1/vehicles`.
- `404 Station not found`: use a real station ID from `/api/v1/stations`.
- `422 Unprocessable Entity`: check allowed severity and status values.
- Empty workflow lists: create records with the POST examples.

### Git Commit:

```bash
git commit -m "phase-3 defect alert and investigation apis"
```

## Phase 4: Simulated Manufacturing Event Generator

### Video Title:

Build a Manufacturing Event Generator with Python and Pydantic

### Goal of This Phase:

Create a standalone event generator that prints realistic manufacturing station, sensor reading, inspection, and defect events as JSON.

### What We Build:

- `event-generator/` Python package.
- Pydantic event schemas for `BaseEvent`, `StationEvent`, `SensorReadingEvent`, and `DefectEvent`.
- Deterministic event generation for stable tests and demos.
- Random event generation for realistic local examples.
- Optional JSON Lines output.
- Tests for schemas, generation, and CLI behavior.

### Why This Matters for Manufacturing Quality:

Manufacturing quality platforms need event data before they can detect patterns, raise alerts, or stream records into downstream systems. Simulated events let us build and test that data flow before connecting to shop-floor equipment.

### Code Walkthrough:

1. Review that the backend still lives in `backend/`.
2. Create the standalone `event-generator/` package.
3. Define the base event contract in `schemas/events.py`.
4. Add station, sensor, and defect generation helpers.
5. Add deterministic and random scenarios.
6. Add the CLI in `app/main.py`.

### Testing Walkthrough:

Run:

```powershell
cd event-generator
pip install -e .
pytest
```

Explain how tests validate UUIDs, timestamps, payload types, deterministic output, random counts, and CLI exit codes.

### Manual Demo:

```powershell
cd event-generator
python -m app.main --mode deterministic
python -m app.main --mode random --count 10
python -m app.main --mode deterministic --output events.jsonl
Get-Content events.jsonl
```

### Common Errors:

- `ModuleNotFoundError: pydantic`: run `pip install -e .` or `pip install pydantic pytest`.
- `No module named app.main`: run from the `event-generator` folder.
- JSON serialization issues with UUID or datetime: use `model_dump_json()` or the CLI output.
- Invalid event count: pass a positive number to `--count`.
- Kafka confusion: Kafka is intentionally not connected until Phase 5.

### Git Commit:

```bash
git commit -m "phase-4 simulated manufacturing event generator"
```

## Phase 5: Redpanda Event Streaming Producer

### Video Title:

Publish Manufacturing Quality Events to Redpanda with Python

### Goal of This Phase:

Connect the simulated event generator to Redpanda so generated manufacturing events can be published to Kafka-compatible topics.

### What We Build:

- Kafka producer wrapper using `kafka-python-ng`.
- Topic routing service.
- Publish mode for the event generator CLI.
- Redpanda Console service in Docker Compose.
- Makefile shortcuts for starting streaming, creating topics, and producing events.
- Mock producer tests that do not require Redpanda.

### Why This Matters for Manufacturing Quality:

Manufacturing systems are event-driven. Station activity, sensor readings, inspections, and defects happen continuously. Kafka-style streaming lets those events move through the platform as they happen.

### Code Walkthrough:

1. Confirm Phase 4 event schemas stay in place.
2. Add `kafka_producer.py`.
3. Add topic routing in `event_publisher.py`.
4. Update the CLI with `--publish` and `--broker`.
5. Add Redpanda Console to Docker Compose.
6. Add Makefile streaming commands.

### Testing Walkthrough:

Run:

```powershell
cd event-generator
pytest
```

Explain topic routing tests, mock producer tests, broker configuration tests, and CLI publish tests.

### Manual Demo:

```powershell
docker compose up redpanda redpanda-console
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
python -m app.main --mode random --count 10 --publish --broker localhost:19092
```

Open Redpanda Console at http://localhost:8080 and inspect:

- `station.events`
- `sensor.readings`
- `quality.defects`

### Common Errors:

- Redpanda container not running: start `redpanda` and `redpanda-console`.
- Wrong broker port: use `localhost:19092`.
- Topic does not exist: run the topic creation command.
- Producer dependency install issue: run `pip install pydantic pytest kafka-python-ng`.
- `confluent-kafka` wheel/build issue on Windows: this project uses `kafka-python-ng`.
- No events visible: check the topic that matches the event type.
- Published but not saved to database: persistence starts in Phase 6.

### Git Commit:

```bash
git commit -m "phase-5 redpanda event streaming producer"
```

## Phase 6: Worker Consumers and Event Persistence

### Video Title:

Persist Manufacturing Quality Events from Redpanda to PostgreSQL

### Goal of This Phase:

Build a standalone Python worker that consumes Redpanda/Kafka events and persists station events, sensor readings, and defect events into PostgreSQL.

Detailed guide: `docs/phase6.md`

### What We Build:

- `worker/` Python package.
- Kafka consumer configuration using the same `kafka-python-ng` client as Phase 5.
- Topic-specific consumers for `station.events`, `sensor.readings`, and `quality.defects`.
- Event mapper service that validates incoming JSON and maps payloads to persistence data.
- Persistence service that writes to `production_events`, `sensor_readings`, and `defects`.
- Idempotency checks based on `event_id`.
- Invalid-event logging with a dead-letter placeholder.
- Worker unit tests that do not require a live Redpanda broker.

### Why This Matters for Manufacturing Quality:

Manufacturing quality systems need streamed shop-floor events to become durable facts. Once station movement, equipment readings, and defects are stored in PostgreSQL, APIs and later analytics can inspect what happened on a vehicle, at a station, or on a piece of equipment.

### Code Walkthrough:

1. Confirm the FastAPI app is in `backend/`, not `api/`.
2. Review Phase 5 topic routing from the event generator.
3. Add the Phase 6 backend migration for `event_id` and ingestion timestamp columns.
4. Create the worker package and CLI.
5. Add mapper functions for station, sensor reading, and defect events.
6. Add the persistence service and explain idempotency.
7. Add topic consumers and the dispatcher.
8. Explain why the worker does not create quality alerts yet.

### Testing Walkthrough:

Run:

```powershell
cd worker
pip install -e .
pytest
```

Then run the existing suites:

```powershell
cd backend
pytest
```

```powershell
cd event-generator
pytest
```

Explain that worker tests use in-memory SQLite and mocked Kafka setup so normal unit tests do not require Docker or Redpanda.

### Manual Demo:

Start services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed database:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

Start API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start worker:

```powershell
cd worker
pip install -e .
python -m app.main
```

Produce demo events:

```powershell
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

Verify:

```powershell
curl http://localhost:8000/api/v1/defects
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/vehicles
docker compose exec postgres psql -U quality -d quality
```

```sql
select count(*) from production_events;
select count(*) from sensor_readings;
select count(*) from defects;
```

### Common Errors:

- Worker cannot connect to Redpanda: confirm `docker compose up postgres redpanda redpanda-console` is running.
- Wrong Kafka broker port: use `localhost:19092` from the host.
- Topics do not exist: run the `rpk topic create` command.
- Worker cannot connect to PostgreSQL: confirm the `postgres` service is running.
- `DATABASE_URL` is wrong: the repo default is `postgresql+psycopg2://quality:quality@localhost:5432/quality`.
- Migrations not run: run `alembic upgrade head` from `backend/`.
- Seed data missing: run `python -m app.db.seed`.
- Foreign key errors from unknown vehicle/station/equipment IDs: publish deterministic demo events or add matching seed data.
- Duplicate `event_id` handling confusion: duplicate messages are logged and skipped by design.
- No defect visible because event did not map to valid seeded IDs: check event `vehicle_id`, `station_id`, `equipment_id`, and payload natural keys.
- No quality alerts visible: alerts are intentionally not generated until Phase 7.

### Git Commit:

```bash
git commit -m "phase-6 worker consumers and event persistence"
```

## Phase 7: Rule-Based Quality Alert Engine

### Video Title:

Build a Rule-Based Manufacturing Quality Alert Engine

### Goal of This Phase:

Add deterministic quality intelligence to the worker so persisted defects, sensor readings, and production events can generate quality alerts.

Detailed guide: `docs/phase7.md`

### What We Build:

- `worker/app/rules/` rule engine package.
- Repeated station defect rule.
- Equipment temperature threshold rule.
- Torque out-of-tolerance rule.
- Low vision confidence rule.
- Same-code defect spike rule.
- Consecutive inspection failure rule.
- Alert persistence service for `quality_alerts`.
- Duplicate open alert prevention.
- `quality.alerts` publishing when alerts are created.
- `defect-spike` event-generator mode for deterministic demos.

### Why This Matters for Manufacturing Quality:

Before AI or machine learning, quality teams need deterministic rules that are explainable and repeatable. A known tolerance breach, a defect spike, or repeated failures at a station should create the same alert every time, with evidence that engineers can inspect.

### Code Walkthrough:

1. Review the Phase 6 worker flow.
2. Add alert candidates and the rule engine.
3. Add each rule module and explain its threshold.
4. Add the alert service and duplicate prevention.
5. Publish created alerts to `quality.alerts`.
6. Wire rule execution after successful event persistence.
7. Add `defect-spike` mode to the event generator.
8. Confirm no frontend dashboard work is added in Phase 7.

### Testing Walkthrough:

Run worker tests:

```powershell
cd worker
pytest
```

Run event-generator tests:

```powershell
cd event-generator
pytest
```

Run backend tests:

```powershell
cd backend
pytest
```

Explain how each rule has a trigger test and a below-threshold test, and how alert persistence, duplicate prevention, publisher calls, and rule-engine integration are tested.

### Manual Demo:

Start services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed database:

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

Start API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start worker:

```powershell
cd worker
pip install -e .
python -m app.main
```

Produce deterministic defect spike:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Verify alerts:

```powershell
curl http://localhost:8000/api/v1/alerts
docker compose exec redpanda rpk topic consume quality.alerts --num 5
```

### Common Errors:

- No alerts created because threshold was not reached: use `--mode defect-spike`.
- Defect spike uses IDs not present in seed data: run `python -m app.db.seed`.
- Worker not running: start `python -m app.main` from `worker/`.
- Redpanda topic missing: create topics with `rpk topic create`.
- `quality.alerts` topic not created: include it in the topic creation command.
- Duplicate alerts appearing repeatedly: confirm the existing open alert duplicate check is active.
- Alerts created in DB but not visible because API is pointing at wrong database: align backend and worker `DATABASE_URL`.
- Sensor payload missing `lower_limit` or `upper_limit`: torque rules fall back to `40.0` and `45.0`.

### Git Commit:

```bash
git commit -m "phase-7 rule based quality alert engine"
```

## Phase 8: React Frontend Foundation

### Video Title:

Build the React Frontend Foundation for a Manufacturing Quality Dashboard

### Goal of This Phase:

Create the frontend dashboard shell with routing, reusable components, API client structure, and tests without connecting live backend data yet.

Detailed guide: `docs/phase8.md`

### What We Build:

- Vite React + TypeScript frontend structure.
- React Router route configuration.
- TanStack Query client setup for Phase 9.
- Sidebar dashboard layout.
- Page header, stat card, data table, status badge, severity badge, loading state, and error state components.
- Placeholder pages for dashboard, stations, equipment, vehicles, defects, alerts, and investigations.
- API service files for future backend integration.
- Frontend tests with Vitest and React Testing Library.

### Why This Matters for Manufacturing Quality:

Quality teams need a clear operational interface for station health, equipment, vehicles, defects, alerts, and investigations. Phase 8 builds the navigation and component foundation first so Phase 9 can focus on live data instead of layout plumbing.

### Code Walkthrough:

1. Confirm the existing `frontend/` Vite app.
2. Add React Router and TanStack Query.
3. Create `AppLayout`, `Sidebar`, and `PageHeader`.
4. Create reusable UI components.
5. Add routed feature pages.
6. Add API client service files using `VITE_API_BASE_URL`.
7. Explain why pages use mock/static data in Phase 8.
8. Confirm live backend data starts in Phase 9.

### Testing Walkthrough:

Run:

```powershell
cd frontend
npm install
npm run test
```

Explain that tests verify app rendering, dashboard routing, sidebar links, mock stat cards, badges, loading and error states, and API base URL behavior.

### Manual Demo:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Click:

- Dashboard
- Stations
- Equipment
- Vehicles
- Defects
- Alerts
- Investigations

### Common Errors:

- Node.js not installed: install Node.js 20 or newer.
- `npm install` fails: rerun from the `frontend/` folder.
- Port 5173 already in use: run `npm run dev -- --port 5174`.
- Vite dev server starts but page is blank: check the console for import or route errors.
- React Router route not found: open `/dashboard`.
- Vitest cannot find jsdom: run `npm install`.
- Testing Library import errors: confirm `src/setupTests.ts` imports `@testing-library/jest-dom/vitest`.
- `VITE_API_BASE_URL` missing: Phase 8 falls back to `http://localhost:8000`.
- Backend not running: Phase 8 still works with placeholders.

### Git Commit:

```bash
git commit -m "phase-8 react frontend foundation"
```

## Phase 9: Frontend Dashboard Data Integration

### Video Title:

Connect a React Manufacturing Dashboard to Live FastAPI Data

### Goal of This Phase:

Turn the Phase 8 frontend shell into a working internal dashboard that reads live manufacturing quality data from the FastAPI backend.

Detailed guide: `docs/phase9.md`

### What We Build:

- TanStack Query calls for dashboard metrics and routed pages.
- API client functions for health, stations, equipment, vehicles, defects, alerts, and investigations.
- Live dashboard cards for vehicles, open defects, open alerts, critical alerts, top defect station, and latest sensor event availability.
- Stations and equipment tables populated from backend API data.
- Vehicles page with VIN search, selected vehicle details, selected vehicle defects, and current station.
- Defects page with severity and status filters.
- Alerts page with severity and status filters plus an acknowledge mutation.
- Investigations table using the backend investigation worklist.
- Frontend tests with mocked API responses.

### Why This Matters for Manufacturing Quality:

Quality teams need the dashboard to reflect the current plant state, not static placeholders. Phase 9 connects the user interface to the backend system of record so station counts, vehicle context, defects, alerts, and investigations can be reviewed in one place.

TanStack Query keeps server state predictable by handling loading, error, success, refetch, and mutation flows. That gives the app a clean foundation before search and deeper investigation workflows are added later.

### Code Walkthrough:

1. Confirm the FastAPI backend lives in `backend/`.
2. Review the Phase 8 React Router routes and reusable components.
3. Update the API client around `VITE_API_BASE_URL`.
4. Add service functions for the backend routes.
5. Replace placeholder page data with TanStack Query calls.
6. Explain dashboard metric calculations from vehicles, defects, alerts, and stations.
7. Add defect and alert filters.
8. Add the alert acknowledge mutation and query invalidation.
9. Explain why Elasticsearch search waits until Phase 10.
10. Explain why the full investigation detail workflow waits until Phase 11.

### Testing Walkthrough:

Run:

```powershell
cd frontend
npm install
npm run test
```

Explain that frontend tests mock `fetch`, so the backend does not need to be running for automated checks. Show tests for API URLs, dashboard loading and error states, live stat calculations, page tables, filters, VIN search, alert acknowledgement, and investigations.

Run existing backend, worker, and event-generator tests when validating the full repo:

```powershell
cd backend
pytest
```

```powershell
cd worker
pytest
```

```powershell
cd event-generator
pytest
```

### Manual Demo:

Start services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed:

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

Start backend API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Optional demo data flow:

```powershell
cd worker
python -m app.main
```

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Click through dashboard, stations, equipment, vehicles, defects, alerts, and investigations. Acknowledge an open alert and confirm the table refreshes.

### Common Errors:

- Frontend cannot connect to backend: confirm the backend is running on port 8000.
- Wrong `VITE_API_BASE_URL`: set it to `http://localhost:8000`.
- Backend not running: start `python -m uvicorn app.main:app --reload --port 8000` from `backend/`.
- CORS error: confirm the backend allows `http://localhost:5173`.
- Database not seeded: run `alembic upgrade head` and `python -m app.db.seed` from `backend/`.
- No defects or alerts visible because worker/event generator has not run: start the worker and publish defect-spike demo events.
- Alert acknowledge fails because PATCH endpoint is missing or wrong: confirm `PATCH /api/v1/alerts/{id}/status` exists.
- React Query cache not refreshing after mutation: invalidate the `alerts` query after acknowledgement.
- Port 5173 already in use: run `npm run dev -- --port 5174`.
- Port 8000 already in use: stop the existing backend process or choose a different backend port and update `VITE_API_BASE_URL`.

### Git Commit:

```bash
git commit -m "phase-9 frontend dashboard data integration"
```

## Phase 10: Elasticsearch Quality Investigation Search

### Video Title:

Build Elasticsearch Search for Manufacturing Quality Investigations

### Goal of This Phase:

Add Elasticsearch indexing and search so engineers can find historical defects, alerts, investigations, and event summaries by VIN, station, equipment, defect code, alert text, investigation text, and free-text descriptions.

Detailed guide: `docs/phase10.md`

### What We Build:

- Backend search package for Elasticsearch client setup, indexing, reindexing, and query service.
- Search document builders for defects, alerts, investigations, and production event summaries.
- Reindex command that reads PostgreSQL and writes Elasticsearch documents.
- Search endpoints for grouped and specialized results.
- Frontend `/search` route.
- Sidebar Search link.
- Search page with input, submit button, loading state, error state, grouped results, and no-results state.
- Backend tests with mocked Elasticsearch.
- Frontend tests with mocked API responses.

### Why This Matters for Manufacturing Quality:

Quality engineers need to look across many record types when investigating a recurring issue. A VIN, station code, equipment tag, defect code, or phrase in an alert description may appear in different tables. Elasticsearch gives the project a purpose-built search index while PostgreSQL remains the system of record.

### Code Walkthrough:

1. Confirm the FastAPI backend lives in `backend/`.
2. Review the existing Elasticsearch service in Docker Compose.
3. Add the backend Elasticsearch dependency.
4. Add search document builders for defects, alerts, investigations, and event summaries.
5. Add a reindex command with `python -m app.search.reindex`.
6. Add FastAPI search endpoints under `/api/v1/search`.
7. Add the frontend search API service.
8. Add `/search` to React Router and Sidebar.
9. Build the Search page with grouped results.
10. Confirm no Phase 11 investigation lifecycle or Phase 12 AI summary work is added.

### Testing Walkthrough:

Run backend tests:

```powershell
cd backend
pytest
```

Explain that backend tests use mocked Elasticsearch clients. They verify empty-query validation, grouped response shape, specialized endpoints, document builders, service hit parsing, missing-index behavior, and empty reindex behavior.

Run frontend tests:

```powershell
cd frontend
npm install
npm run test
```

Explain that frontend tests mock `fetch` and cover page render, search input, submit behavior, loading state, error state, grouped results, no results, and sidebar navigation.

### Manual Demo:

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

Optional demo events:

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

Test backend search:

```powershell
curl "http://localhost:8000/api/v1/search?q=torque"
curl "http://localhost:8000/api/v1/search/defects?q=torque"
curl "http://localhost:8000/api/v1/search/alerts?q=defect"
curl "http://localhost:8000/api/v1/search/investigations?q=root"
```

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173/search
```

### Common Errors:

- Elasticsearch container not running: start it with `docker compose up postgres elasticsearch`.
- Wrong `ELASTICSEARCH_URL`: set it to `http://localhost:9200`.
- Elasticsearch security enabled accidentally: confirm `xpack.security.enabled=false` in Docker Compose.
- Index does not exist: run `python -m app.search.reindex`.
- No search results because reindex was not run: run the reindex command after creating demo data.
- No search results because database has no demo defects or alerts: seed data and run worker/event-generator demos.
- Backend CORS issue from frontend search page: confirm `FRONTEND_ORIGIN=http://localhost:5173`.
- Frontend search error because backend is not running: start the API on port 8000.
- Search endpoint returns 400 for empty query: submit a non-empty query.

### Git Commit:

```bash
git commit -m "phase-10 elasticsearch quality investigation search"
```

## Phase 11: Quality Investigation Workflow

### Video Title:

Build the Engineer Quality Investigation Workflow

### Goal of This Phase:

Create the complete manual investigation workflow that lets quality engineers move from an alert to an investigation, review evidence, update notes and root-cause hypotheses, change statuses, and resolve the investigation and related alert.

Detailed guide: `docs/phase11.md`

### What We Build:

- `POST /api/v1/alerts/{id}/investigation`.
- `PATCH /api/v1/investigations/{id}/status`.
- Investigation update behavior that refreshes `updated_at`.
- Resolution behavior that sets `closed_at` and resolves the related alert.
- Duplicate active investigation prevention for the same alert.
- Alert detail page.
- Investigation detail page.
- Investigation form.
- Evidence panel.
- Timeline panel.
- Alert and investigation status action panels.
- Search result links into alert and investigation detail routes.
- Backend and frontend tests for the workflow.

### Why This Matters for Manufacturing Quality:

Alerts tell engineers that something needs attention. Investigations are where the quality team records what they learned, what they believe caused the issue, and whether the issue is contained or resolved.

The workflow keeps evidence attached to the investigation so engineers do not lose the facts that triggered the alert.

### Code Walkthrough:

1. Confirm the backend lives in `backend/`.
2. Review existing alert and investigation models.
3. Add the create-from-alert endpoint.
4. Copy `evidence_json` from alert to investigation.
5. Prevent duplicate active investigations.
6. Add investigation status endpoint.
7. Resolve the related alert when an investigation is resolved.
8. Add alert and investigation detail frontend routes.
9. Add evidence and timeline panels.
10. Confirm no Phase 12 AI summary generation is added.

### Testing Walkthrough:

Run backend tests:

```powershell
cd backend
pytest
```

Explain tests for create-from-alert, missing alerts, duplicate active investigations, update summary, update root-cause hypothesis, status validation, resolution, alert resolution, and evidence detail.

Run frontend tests:

```powershell
cd frontend
npm install
npm run test
```

Explain tests for alert detail, evidence panel, create form, create mutation, investigation detail, edit form, status update, timeline, and search result detail routing.

### Manual Demo:

Start services:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Run backend setup:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
pytest
python -m uvicorn app.main:app --reload --port 8000
```

Create alert data with the Phase 7 defect spike or direct API POST.

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173/alerts
```

Demo steps:

1. Open Alerts.
2. Click an alert.
3. Review evidence.
4. Click Create Investigation.
5. Enter title, summary, and root-cause hypothesis.
6. Save the investigation.
7. Open investigation detail.
8. Edit the summary or hypothesis.
9. Resolve the investigation.
10. Confirm the related alert is resolved.

### Common Errors:

- No alerts exist to investigate: create an alert through the API or run the Phase 7 defect spike.
- Alert ID not found: use an ID returned from `/api/v1/alerts`.
- Duplicate investigation already exists for alert: open the existing active investigation or resolve it first.
- Investigation status validation fails: use `draft`, `active`, `waiting_on_data`, or `resolved`.
- Frontend route does not load because route path is missing: confirm `/alerts/:id` and `/investigations/:id` are registered.
- Mutation succeeds but UI does not refresh: invalidate related alert and investigation queries after mutation.
- CORS error: confirm `FRONTEND_ORIGIN=http://localhost:5173`.
- Backend not running: start `python -m uvicorn app.main:app --reload --port 8000`.
- Database not migrated: run `alembic upgrade head`.
- Seed data missing: run `python -m app.db.seed`.

### Git Commit:

```bash
git commit -m "phase-11 quality investigation workflow"
```

## Phase 12: AI-Assisted Investigation Summary

### Video Title:

Build Evidence-Grounded AI Investigation Summaries

### Goal of This Phase:

Add AI-assisted investigation summary generation using only platform evidence from alerts, defects, sensor readings, station events, and investigation notes.

Detailed guide: `docs/phase12.md`

### What We Build:

- `investigations.ai_summary` JSON persistence.
- Alembic migration for the AI summary column.
- AI provider interface.
- Deterministic mock summary provider.
- OpenAI-compatible provider placeholder.
- Evidence gathering service for investigations.
- `POST /api/v1/investigations/{id}/ai-summary`.
- Frontend Generate AI Summary button.
- AI Summary panel with likely issue, evidence, recommended checks, confidence, and limitations.
- Backend guardrail tests.
- Frontend AI summary panel tests.

### Why This Matters for Manufacturing Quality:

AI can help engineers organize evidence quickly, but it must not become an unsupported authority. Phase 12 keeps the summary grounded in platform records and always shows limitations so engineers know what evidence was missing.

The mock provider keeps the project demoable without paid APIs or external keys.

### Code Walkthrough:

1. Confirm the backend lives in `backend/`.
2. Add `ai_summary` to the investigation model and migration.
3. Add typed AI summary schemas.
4. Add provider interface and mock provider.
5. Add evidence gathering from alert, defects, sensor readings, station events, and investigation notes.
6. Add the AI summary endpoint.
7. Save summary JSON on the investigation.
8. Add the frontend API mutation.
9. Add the AI Summary panel to Investigation Detail.
10. Confirm no Phase 13 E2E tests are added.

### Testing Walkthrough:

Run backend tests:

```powershell
cd backend
pytest
```

Explain tests for structured summary output, alert evidence, defect evidence, sensor evidence, limitations, no-hallucination guardrails, confidence levels, endpoint success, persistence, and no external network calls.

Run frontend tests:

```powershell
cd frontend
npm install
npm run test
```

Explain tests for the generate button, mutation call, loading state, error state, displayed likely issue, evidence, next checks, confidence, limitations, and existing saved summary display.

### Manual Demo:

Start services:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Run backend setup:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
pytest
python -m uvicorn app.main:app --reload --port 8000
```

Create alert and investigation data through the UI or existing APIs, then generate by API:

```powershell
curl -X POST http://localhost:8000/api/v1/investigations/REPLACE_WITH_INVESTIGATION_ID/ai-summary
```

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173/investigations
```

Open an investigation detail page and click Generate AI Summary.

### Common Errors:

- No investigation exists: create one from an alert first.
- Investigation has no linked alert: create investigations through the alert workflow when possible.
- No `evidence_json` available: the summary will include limitations.
- Summary appears too generic because evidence is thin: ingest or create more relevant defects, readings, and events.
- AI summary not saved because `ai_summary` field is missing: run `alembic upgrade head`.
- Migration needed for `ai_summary` column: run backend migrations.
- Frontend mutation succeeds but page does not refresh: invalidate investigation detail queries after mutation.
- Backend not running: start `python -m uvicorn app.main:app --reload --port 8000`.
- CORS error: confirm `FRONTEND_ORIGIN=http://localhost:5173`.
- Developer expected OpenAI API but project defaults to mock provider: set `AI_SUMMARY_PROVIDER=mock` for local demos.

### Git Commit:

```bash
git commit -m "phase-12 ai assisted investigation summaries"
```

## Phase 13: End-to-End Testing

### Video Title:

Build Playwright End-to-End Tests for a Manufacturing Quality Workflow

### Goal of This Phase:

Add browser automation that proves the dashboard, alert workflow, investigation creation, AI summary generation, and investigation resolution work together against the running FastAPI backend and React frontend.

Detailed guide: `docs/phase13.md`

### What We Build:

- `e2e/` Playwright project.
- `manufacturing-quality-flow.spec.ts`.
- API helper for backend health checks and alert fixture creation.
- Test-data helper for deterministic manufacturing workflow payloads.
- Stable frontend selectors for key dashboard, alert, investigation, AI summary, and resolution controls.
- `make test-e2e` shortcut.
- Documentation for automated E2E and manual full-system demos.

### Why This Matters for Manufacturing Quality:

Unit and integration tests prove important pieces work, but quality teams care about the complete path: an alert appears, an engineer opens it, creates an investigation, asks for an evidence-grounded summary, and resolves the issue. Playwright tests that story through the browser.

### Code Walkthrough:

1. Confirm the FastAPI backend lives in `backend/`.
2. Add stable `data-testid` selectors where the workflow needs reliable anchors.
3. Create the `e2e/` package with `@playwright/test`.
4. Configure Playwright with `baseURL = http://localhost:5173`.
5. Add API helpers for `E2E_API_URL=http://localhost:8000`.
6. Create alert fixtures through the backend API.
7. Drive the dashboard, alerts, alert detail, investigation form, AI summary panel, and resolution button.
8. Explain why the automated test does not depend on Redpanda timing.
9. Show the separate manual full-system demo with event-generator, Redpanda, worker, database, API, and UI.
10. Confirm Phase 14 one-command demo orchestration is not added yet.

### Testing Walkthrough:

Start backend:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Run Playwright:

```powershell
cd e2e
npm install
npx playwright install
npx playwright test
```

Explain that Playwright uses screenshots and videos on failure, and traces on retry. Show `e2e/test-results/` and `e2e/playwright-report/` after a failure.

### Manual Demo:

Start services:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Run backend setup and API:

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

Start worker:

```powershell
cd worker
pip install -e .
python -m app.main
```

Publish demo events:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173/alerts`, open an alert, create an investigation, generate an AI summary, and resolve the investigation.

### Common Errors:

- Backend not running: start `python -m uvicorn app.main:app --reload --port 8000` from `backend/`.
- Frontend not running: start `npm run dev` from `frontend/`.
- Playwright browsers missing: run `npx playwright install` from `e2e/`.
- Database not seeded: run `alembic upgrade head` and `python -m app.db.seed` from `backend/`.
- E2E cannot find alert data: confirm `POST /api/v1/alerts` succeeds and the frontend uses `VITE_API_BASE_URL=http://localhost:8000`.
- Manual demo has no alerts: run the worker and publish `defect-spike` events.
- Redpanda topic missing: create topics with `rpk topic create`.
- Duplicate active investigation: use the API-created fixture flow or resolve the existing investigation.
- Failed test needs debugging: inspect `e2e/test-results/` artifacts and the HTML report.

### Git Commit:

```bash
git commit -m "phase-13 end to end manufacturing quality workflow tests"
```
