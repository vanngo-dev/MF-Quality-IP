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

## Phase 6 Worker Consumer Coverage

Worker tests verify:

- Station events map to production event persistence data.
- Sensor reading events map to sensor reading persistence data.
- Defect events map to defect persistence data.
- Duplicate `event_id` values are ignored safely.
- Invalid station events are rejected and can be logged.
- Invalid sensor reading events are rejected and can be logged.
- Invalid defect events are rejected and can be logged.
- The persistence service saves a production event.
- The persistence service saves a sensor reading.
- The persistence service saves a defect.
- Worker configuration loads broker and database URL from environment variables.
- Consumer topic subscription configuration includes `station.events`, `sensor.readings`, and `quality.defects`.
- Kafka consumer setup is tested with a mocked Kafka module, not a live Redpanda broker.

See `docs/phase6.md` for the dedicated Phase 6 worker test and manual verification guide.

## Phase 7 Rule Engine Coverage

Rule engine tests verify:

- Repeated defects at the same station trigger `REPEATED_DEFECT_STATION`.
- Repeated defect station rule stays quiet below threshold.
- Equipment temperature readings above threshold trigger `EQUIPMENT_TEMPERATURE_HIGH`.
- Temperature readings below threshold do not trigger.
- Torque readings outside tolerance trigger `TORQUE_OUT_OF_TOLERANCE`.
- Torque readings inside tolerance do not trigger.
- Vision confidence below threshold triggers `VISION_CONFIDENCE_LOW`.
- Vision confidence above threshold does not trigger.
- Same-code defect spikes trigger `DEFECT_CODE_SPIKE`.
- Defect spike rule stays quiet below threshold.
- Consecutive inspection failures trigger `CONSECUTIVE_INSPECTION_FAILURES`.
- Mixed pass/fail inspection sequences do not trigger.
- Alert persistence works.
- Duplicate open alert prevention works.
- `quality.alerts` publish function is called when an alert is created.
- Rule engine can run after event persistence.
- Invalid or incomplete data does not crash the rule engine.

Event-generator tests verify `defect-spike` mode and mock publishing counts.

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

Worker:

```powershell
cd worker
pip install -e .
pytest
```

If editable install is not available:

```powershell
pip install pydantic pytest kafka-python-ng sqlalchemy psycopg2-binary
```

Phase 5 uses `kafka-python-ng` for the real producer. Phase 6 uses the same `kafka-python-ng` client for the worker consumer.

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

## Worker Manual Verification

Automated worker tests do not require Redpanda or PostgreSQL. Manual verification uses both services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed data:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start the worker in another terminal:

```powershell
cd worker
pip install -e .
python -m app.main
```

Produce demo events in another terminal:

```powershell
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

Verify API and database state:

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

Expected results:

- Redpanda starts.
- PostgreSQL starts.
- Worker starts without crashing.
- Event generator publishes events.
- Worker consumes events.
- Production events are persisted.
- Sensor readings are persisted.
- Defects are persisted.
- Duplicate event IDs do not create duplicate rows.
- Invalid events are logged and skipped.
- In Phase 6 alone, no quality alerts are generated; Phase 7 adds alert rules after this ingestion flow.

## Rule Engine Manual Verification

Phase 7 manual verification uses the same Redpanda and PostgreSQL services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed data:

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start the worker:

```powershell
cd worker
pip install -e .
python -m app.main
```

Produce deterministic defect spike events:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Verify alerts:

```powershell
curl http://localhost:8000/api/v1/alerts
docker compose exec redpanda rpk topic consume quality.alerts --num 5
```

Expected results:

- Worker persists defect and sensor events.
- Rule engine evaluates persisted data.
- At least one `quality_alerts` row is created.
- The alert is visible through `/api/v1/alerts`.
- `quality.alerts` receives an alert event.
- Running the same defect spike twice does not create duplicate open alerts for the same condition.

See `docs/phase7.md` for the dedicated Phase 7 guide.
