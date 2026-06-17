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
