# Testing Strategy

## Phase 2 Coverage

Backend tests verify:

- Database configuration imports correctly.
- SQLAlchemy ORM models import correctly.
- Phase 1 health endpoints still pass.
- Seed data can be created.
- Read-only domain API endpoints return the expected seeded data.
- Vehicle lookup by VIN returns a vehicle.
- Unknown VIN lookup returns `404`.

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
