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
