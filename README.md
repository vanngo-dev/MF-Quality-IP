# Manufacturing Quality Intelligence Platform

Full-stack portfolio project for manufacturing quality workflows, event-driven ingestion, investigation summaries, and operational dashboards.

## Current Phase

Phase 4 adds a standalone simulated manufacturing event generator on top of the Phase 1-3 backend foundation:

- FastAPI backend with a health contract.
- React + TypeScript + Vite frontend status surface.
- PostgreSQL, Redpanda, and Elasticsearch local services through Docker Compose.
- SQLAlchemy ORM models for plants, production lines, stations, equipment, vehicles, events, readings, defects, alerts, and investigations.
- Alembic migration for the initial domain schema.
- Seed data for local demos and tests.
- Read-only `/api/v1` endpoints for the manufacturing domain.
- Defect, quality alert, and investigation REST APIs.
- Business validation for workflow severity, status, and foreign-key references.
- Python event generator for station, sensor reading, inspection, and defect events.
- Deterministic and random JSON event output for tests, demos, and future streaming.
- Backend and frontend automated tests.
- GitHub Actions CI for backend and frontend checks.
- Documentation and YouTube tutorial notes.

Detailed notes:

- `docs/phase-01-foundation.md`
- `docs/phase-02-postgres-domain-models.md`
- `docs/phase-03-quality-workflow-apis.md`
- `docs/phase-04-simulated-event-generator.md`
- `docs/architecture.md`
- `docs/event-contracts.md`
- `docs/data-model.md`
- `docs/api-contracts.md`
- `docs/testing-strategy.md`

## Repository Structure

```text
backend/              FastAPI application and backend tests
event-generator/      Standalone simulated manufacturing event generator
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

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend app:

- http://localhost:5173

## Local Services

```powershell
docker compose up -d postgres redpanda elasticsearch
```

Services:

- PostgreSQL: localhost:5432
- Redpanda: localhost:9092
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
pip install fastapi "uvicorn[standard]" pytest httpx pydantic-settings sqlalchemy alembic psycopg2-binary
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

Phase 4 does not publish to Kafka yet. It prints valid JSON events to the console or to a JSON Lines file.

```powershell
cd event-generator
pip install -e .
pytest
python -m app.main --mode deterministic
python -m app.main --mode random --count 10
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
