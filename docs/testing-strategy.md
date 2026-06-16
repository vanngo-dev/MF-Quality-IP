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

## Phase 4 Event Generator Coverage

Event generator tests verify:

- Base event schema validates a valid event.
- Base event schema rejects missing `event_id`.
- Base event schema rejects invalid timestamps.
- Station event payloads validate.
- Sensor reading type and value validation works.
- Defect severity and defect code validation works.
- Deterministic generation returns the expected six events.
- Deterministic generation includes station, sensor, inspection, and defect events.
- Random generation respects the requested count.
- Random generation produces valid event schemas.
- Invalid random counts fail cleanly.
- CLI deterministic and random modes exit successfully.

## Phase 5 Streaming Producer Coverage

Producer tests verify:

- Phase 4 deterministic generation still works.
- Phase 4 random generation still works.
- Station events route to `station.events`.
- Sensor readings route to `sensor.readings`.
- Defect events route to `quality.defects`.
- Unknown event types fail clearly.
- Broker configuration loads from CLI input or `KAFKA_BOOTSTRAP_SERVERS`.
- Mock producer receives the expected topic and JSON payload.
- Publish mode validates events before publishing.
- Publish CLI deterministic and random modes exit successfully with the mock producer.

## Local Test Command

Backend:

```powershell
cd backend
pytest
```

Event generator:

```powershell
cd event-generator
pip install -e .
pytest
```

If editable install is not available:

```powershell
pip install pydantic pytest
```

Phase 5 uses `kafka-python-ng` for the real producer:

```powershell
pip install pydantic pytest kafka-python-ng
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

## Streaming Manual Verification

Automated streaming tests use a mock producer so Redpanda is not required for normal test runs.

Manual streaming verification uses Redpanda:

```powershell
docker compose up redpanda redpanda-console
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

Then verify with Redpanda Console at http://localhost:8080 or with:

```powershell
docker compose exec redpanda rpk topic consume station.events --num 5
docker compose exec redpanda rpk topic consume sensor.readings --num 5
docker compose exec redpanda rpk topic consume quality.defects --num 5
```
