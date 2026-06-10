# Testing Strategy

## Phase 3 Coverage

Backend tests verify:

- Database configuration imports correctly.
- SQLAlchemy ORM models import correctly.
- Phase 1 health endpoints still pass.
- Seed data can be created.
- Read-only domain API endpoints return the expected seeded data.
- Vehicle lookup by VIN returns a vehicle.
- Unknown VIN lookup returns `404`.
- Defects can be created, listed, and fetched by ID.
- Defect validation rejects invalid vehicle IDs, station IDs, and severity values.
- Alerts can be created, listed, fetched by ID, and updated by status.
- Alert validation rejects invalid station IDs, severity values, and status values.
- Investigations can be created, listed, fetched by ID, and updated.
- Investigation validation rejects invalid alert IDs and status values.

## Local Test Command

```powershell
cd backend
pytest
```

## Database Test Approach

Tests use SQLAlchemy with an in-memory SQLite database. This keeps the tests fast and independent of Docker while still exercising the same ORM models, seed function, and FastAPI dependency injection path.

PostgreSQL is still the application database for local development and demos:

```powershell
docker compose up postgres
cd backend
alembic upgrade head
python -m app.db.seed
```

## Manual Verification

After seeding PostgreSQL and starting the API, call the `/api/v1` endpoints with `curl` and confirm the seeded counts:

- 1 plant
- 2 lines
- 6 stations
- 8 equipment records
- 10 vehicles

Then create one defect, one alert, and one investigation. Confirm invalid IDs return `404` and invalid status or severity values return `422`.
