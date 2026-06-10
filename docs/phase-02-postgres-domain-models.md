# Phase 2: PostgreSQL Database and Domain Models

## Goal

Add PostgreSQL database support, SQLAlchemy ORM models, Alembic migration, seed data, and read-only domain API endpoints.

## What This Phase Establishes

- Database configuration through `DATABASE_URL`.
- SQLAlchemy engine, session, base model, and metadata setup.
- ORM models for the manufacturing quality domain.
- Alembic migration for the first database schema.
- Seed data for demos and automated tests.
- Read-only `/api/v1` endpoints for plants, lines, stations, equipment, and vehicles.

## Why It Matters

Manufacturing quality investigations need context. A defect is more useful when it can be tied to a plant, production line, station, piece of equipment, and vehicle. This phase creates that context as relational data.

## Backend Location

The FastAPI backend is in `backend/`. This project does not use an `api/` folder.

## Run Database and Seed Data

```powershell
docker compose up postgres
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

## Run Tests

```powershell
cd backend
pytest
```

## Run API

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## Manual API Checks

```powershell
curl http://localhost:8000/api/v1/plants
curl http://localhost:8000/api/v1/lines
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/equipment
curl http://localhost:8000/api/v1/vehicles
curl http://localhost:8000/api/v1/vehicles/MQPLANT0000000001
```

## Expected Seed Counts

- 1 plant
- 2 production lines
- 6 stations
- 8 equipment records
- 10 vehicles

## Troubleshooting

- If `pip install -e .` fails, confirm network access to PyPI.
- If `alembic` is not found, run `pip install -e .` from inside `backend`.
- If PostgreSQL cannot start, check whether port `5432` is already in use.
- If `alembic upgrade head` cannot connect, confirm Docker Compose PostgreSQL is running.
- If API endpoints return empty arrays, run `python -m app.db.seed`.
