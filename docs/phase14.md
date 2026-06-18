# Phase 14 — Docker Compose and One-Command Demo

## Goal

Make the full project easy to run from a fresh clone with Docker Compose, Makefile commands, reset commands, seed/demo setup, and clear Windows PowerShell fallback instructions.

This phase stops at local developer experience. It does not add GitHub Actions CI; CI starts in Phase 15. It does not add final portfolio polish; that starts in Phase 16.

## What Was Built

- Dockerfiles for `backend/`, `worker/`, `event-generator/`, and `frontend/`.
- Docker Compose app services for backend, worker, event generator, and frontend.
- Docker Compose health checks for local infrastructure readiness.
- `.env.example` with host-machine URLs and Docker service-to-service URLs.
- Root Makefile commands for install, up, down, reset, migrations, seed data, topics, demo event publishing, tests, E2E, search reindex, demo startup, logs, and status.
- `make demo` wrapper with staged `make demo-infra`, `make demo-data`, and `make demo-app` commands.
- Fresh-clone setup documentation.
- PowerShell fallback instructions for users without Make on Windows.

## Why This Matters for Manufacturing Quality

The platform now includes a backend API, PostgreSQL domain data, Redpanda streaming, a worker, an event generator, Elasticsearch search, a React frontend, AI-assisted summaries, and E2E tests. A quality workflow demo should not require someone to discover the startup order by trial and error.

Phase 14 turns the project into a repeatable local demo:

```text
event-generator -> Redpanda -> worker -> PostgreSQL -> FastAPI -> React UI
                                              |
                                              -> Elasticsearch reindex -> Search UI
```

## Docker Compose Services

The local stack includes:

| Service | Purpose | Local URL or port |
| --- | --- | --- |
| `postgres` | System-of-record database | `localhost:5432` |
| `redpanda` | Kafka-compatible broker | `localhost:19092` |
| `redpanda-console` | Topic inspection UI | `http://localhost:8080` |
| `elasticsearch` | Search index | `http://localhost:9200` |
| `backend` | FastAPI API | `http://localhost:8000` |
| `worker` | Event consumer and alert generator | long-running worker |
| `event-generator` | One-shot demo event producer in the `tools` profile | Makefile-run helper |
| `frontend` | Vite React UI | `http://localhost:5173` |

The backend connects to PostgreSQL with `postgres:5432` inside Docker. The worker connects to Redpanda with `redpanda:9092` inside Docker. The browser still uses host URLs, so the frontend uses `VITE_API_BASE_URL=http://localhost:8000`.

The `event-generator` service is assigned to the `tools` profile because it is a one-shot producer, not a long-running service. Makefile producer commands call it with `docker compose --profile tools run --rm event-generator ...`.

## Makefile Commands

Available commands:

```powershell
make install
make up
make down
make reset
make migrate
make seed
make create-topics
make produce-demo-events
make produce-defect-spike
make test
make test-api
make test-worker
make test-event-generator
make test-frontend
make test-e2e
make reindex-search
make demo
make logs
make status
```

Key commands:

- `make install`: installs local backend, worker, event-generator, frontend, and E2E dependencies.
- `make up`: starts Compose services in detached mode.
- `make down`: stops Compose services.
- `make reset`: runs `docker compose down -v` and deletes local Docker volumes, including PostgreSQL data.
- `make migrate`: runs Alembic migrations in the backend container.
- `make seed`: runs the backend seed script.
- `make create-topics`: creates Redpanda topics.
- `make produce-defect-spike`: publishes deterministic quality events that can trigger alerts.
- `make test`: runs backend, worker, event-generator, and frontend test commands.
- `make test-e2e`: runs Playwright tests separately.
- `make reindex-search`: rebuilds Elasticsearch search documents.
- `make logs`: follows Compose logs.
- `make status`: shows Compose service status.

## Environment Variables

Copy the example environment file:

```powershell
copy .env.example .env
```

Host-machine values:

```text
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/manufacturing_quality
KAFKA_BOOTSTRAP_SERVERS=localhost:19092
ELASTICSEARCH_URL=http://localhost:9200
VITE_API_BASE_URL=http://localhost:8000
E2E_FRONTEND_URL=http://localhost:5173
E2E_API_URL=http://localhost:8000
```

Docker service-to-service values:

```text
DOCKER_DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/manufacturing_quality
DOCKER_KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
DOCKER_ELASTICSEARCH_URL=http://elasticsearch:9200
```

The default local AI summary provider remains:

```text
AI_SUMMARY_PROVIDER=mock
```

## One-Command Demo

Run:

```powershell
make demo
```

The wrapper runs:

```text
make demo-infra
make demo-data
make demo-app
make status
```

This workflow:

1. Starts PostgreSQL, Redpanda, Redpanda Console, and Elasticsearch.
2. Runs backend migrations.
3. Seeds the database.
4. Creates Redpanda topics.
5. Publishes defect-spike demo events.
6. Starts the backend API.
7. Starts the worker.
8. Starts the frontend.
9. Leaves the app in a demo-ready state.

Open:

```text
Frontend: http://localhost:5173
Backend docs: http://localhost:8000/docs
Redpanda Console: http://localhost:8080
Elasticsearch: http://localhost:9200
```

## PowerShell Fallback Demo

Use this path if Make is not installed on Windows.

Start infrastructure:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Backend terminal:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

Create topics in another terminal:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Worker terminal:

```powershell
cd worker
pip install -e .
python -m app.main
```

Event generator terminal:

```powershell
cd event-generator
pip install -e .
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Frontend terminal:

```powershell
cd frontend
npm install
npm run dev
```

## Fresh Clone Setup

```powershell
git clone REPLACE_WITH_REPO_URL
cd manufacturing-quality-intelligence-platform
copy .env.example .env
docker compose config
make demo
```

If local Docker volumes contain old database credentials, run:

```powershell
make reset
```

Then rerun:

```powershell
make demo
```

## How to Run It

Validate Compose:

```powershell
docker compose config
```

Validate the optional tools profile:

```powershell
docker compose --profile tools config
```

Start everything with Docker:

```powershell
make demo
```

Inspect logs:

```powershell
make logs
```

Check service status:

```powershell
make status
```

Rebuild search documents after demo data is available:

```powershell
make reindex-search
```

Run Playwright after backend and frontend are running:

```powershell
make test-e2e
```

## Automated Tests

Recommended checks:

```powershell
docker compose config
Get-Content Makefile
docker compose --profile tools config
```

Existing suites:

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

```powershell
cd frontend
npm run test:run
```

Container builds when Docker can download images and packages:

```powershell
docker compose build backend worker event-generator frontend
```

E2E stays separate from default tests:

```powershell
make test-e2e
```

## Manual Tests

Manual verification checklist:

- Frontend opens.
- Dashboard loads.
- Backend health works.
- Database has seeded data.
- Redpanda topics exist.
- Defect spike can be produced.
- Worker consumes events.
- Alerts appear in the UI.
- Investigation can be created.
- AI summary can be generated.
- Search page works after reindex.
- E2E test can run after backend and frontend are up.

Useful manual checks:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/alerts
docker compose exec redpanda rpk topic list
```

## Expected Results

- `docker compose config` passes.
- `make demo` or the documented PowerShell fallback works.
- App can be started from a fresh clone.
- Dashboard has seeded demo data.
- Alerts exist after the defect spike is processed by the worker.
- Investigation workflow works.
- AI summary workflow works.
- Search works after `make reindex-search`.
- Documentation is clear enough for a recruiter or interviewer to run the project.

## Common Errors and Fixes

- Docker Desktop not running: start Docker Desktop and rerun `docker compose config`.
- Docker Compose config fails: check YAML indentation and environment variable syntax.
- Port 5432 already in use: stop the existing PostgreSQL process or change the Compose port.
- Port 8000 already in use: stop the existing backend process.
- Port 5173 already in use: stop the existing Vite dev server or change the frontend port.
- Port 9200 already in use: stop the existing Elasticsearch process.
- Port 19092 already in use: stop the existing Kafka or Redpanda process.
- Make not installed on Windows: use the PowerShell fallback demo.
- Database connection uses `localhost` inside Docker: use `postgres:5432` inside Docker.
- Kafka broker uses `localhost` inside Docker: use `redpanda:9092` inside Docker.
- Elasticsearch security enabled: keep `xpack.security.enabled=false` for local development.
- Migrations not run: run `make migrate` or `alembic upgrade head`.
- Seed data missing: run `make seed` or `python -m app.db.seed`.
- Topics not created: run `make create-topics`.
- Worker started before topics exist: create topics first, then restart the worker with `docker compose restart worker`.
- Frontend cannot reach backend because `VITE_API_BASE_URL` is wrong: use `http://localhost:8000`.
- Existing Docker volume has old database credentials: run `make reset`, then `make demo`.

## Git Commit

```bash
git commit -m "phase-14 dockerized one command demo workflow"
```
