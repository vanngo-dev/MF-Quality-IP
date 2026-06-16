# Phase 6 — Worker Consumers and Event Persistence

## Goal

Build a Python worker that consumes manufacturing events from Redpanda/Kafka topics and persists them into PostgreSQL.

## What Was Built

Phase 6 adds a standalone `worker/` service that runs separately from the FastAPI backend. The worker subscribes to the Redpanda topics created in Phase 5, validates incoming event payloads, maps each event type to database persistence data, and writes accepted records into PostgreSQL.

The worker includes:

- topic-specific consumers for station events, sensor readings, and defect events
- an event mapper service that validates and translates JSON events
- a persistence service that writes to existing database tables
- idempotency handling based on `event_id`
- invalid event handling that logs bad messages instead of crashing
- unit tests for mapping, persistence, duplicates, invalid events, and configuration

## Why This Matters for Manufacturing Quality

Factory systems emit many operational events while production is running. Vehicles enter stations, tools report sensor readings, inspections complete, and defects are detected continuously.

A background worker lets the platform ingest those events without blocking the API. FastAPI can stay focused on request/response workflows, while the worker handles long-running event consumption, retries, duplicate delivery, and bad messages.

## Architecture Flow

```text
event-generator -> Redpanda topics -> worker consumers -> PostgreSQL -> FastAPI read endpoints
```

## Topics Consumed

- `station.events`
- `sensor.readings`
- `quality.defects`

## Database Tables Written

- `production_events`
- `sensor_readings`
- `defects`

## Worker Responsibilities

- consume events from Redpanda
- validate event payloads
- map events to database records
- persist station events
- persist sensor readings
- persist defects
- ignore duplicate `event_id`
- log invalid events
- avoid crashing on bad messages

## Idempotency Explanation

Kafka-compatible systems can deliver the same message more than once during retries, broker restarts, consumer group rebalances, or local demo reruns. Without idempotency, the same event could create duplicate rows in PostgreSQL.

Phase 6 uses `event_id` as the idempotency key. Before inserting a production event, sensor reading, or defect, the worker checks whether that `event_id` has already been persisted. If it exists, the event is skipped safely and logged as a duplicate.

## How to Run It

Use these Windows-friendly commands from the repository root unless a step says otherwise.

### Start Services

```powershell
docker compose up postgres redpanda redpanda-console
```

### Run Backend Migrations and Seed Data

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

### Start API

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

### Create Topics

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

### Start Worker

```powershell
cd worker
pip install -e .
python -m app.main
```

If editable install is not supported, install the worker dependencies directly:

```powershell
pip install pydantic sqlalchemy psycopg2-binary kafka-python-ng pytest
```

### Produce Events

```powershell
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

## Automated Tests

Phase 6 worker tests cover:

- event mapper tests for station, sensor reading, and defect events
- persistence tests for production events, sensor readings, and defects
- duplicate `event_id` idempotency tests
- invalid event tests for missing or malformed payload fields
- worker configuration tests for broker, database URL, and topic subscription settings
- mocked Kafka consumer setup tests that do not require a live Redpanda broker

Run them with:

```powershell
cd worker
pytest
```

## Manual Tests

Manual verification workflow:

1. Start PostgreSQL and Redpanda.
2. Run migrations.
3. Seed data.
4. Start API.
5. Create topics.
6. Start worker.
7. Publish deterministic events.
8. Verify events were persisted.

## API Verification

```powershell
curl http://localhost:8000/api/v1/defects
```

The current API exposes defects and manufacturing domain records. If direct production event and sensor reading API endpoints do not exist yet, verify `production_events` and `sensor_readings` with database queries.

## Optional Database Verification

This repo's `docker-compose.yml` uses the `quality` database and `quality` user:

```powershell
docker compose exec postgres psql -U quality -d quality
```

If your local environment uses the alternate `manufacturing_quality` database from the original project spec, use:

```powershell
docker compose exec postgres psql -U postgres -d manufacturing_quality
```

Then run:

```sql
select count(*) from production_events;
select count(*) from sensor_readings;
select count(*) from defects;
```

## Expected Results

- worker starts without crashing
- event generator publishes events
- worker consumes `station.events`
- worker consumes `sensor.readings`
- worker consumes `quality.defects`
- station events persist to `production_events`
- sensor readings persist to `sensor_readings`
- defect events persist to `defects`
- duplicate `event_id` does not create duplicate rows
- invalid messages are logged and skipped

## Common Errors and Fixes

### Redpanda is not running

Fix:

```powershell
docker compose up redpanda redpanda-console
```

### Wrong broker port

From the host machine, use the external broker port from `docker-compose.yml`. In this repo, Redpanda advertises:

```text
localhost:19092
```

### Topics do not exist

Check existing topics:

```powershell
docker compose exec redpanda rpk topic list
```

Create missing topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
```

### PostgreSQL is not running

Fix:

```powershell
docker compose up postgres
```

### Migrations were not run

Fix:

```powershell
cd backend
alembic upgrade head
```

### Seed data is missing

Fix:

```powershell
python -m app.db.seed
```

### Foreign key errors

The event IDs for station, vehicle, or equipment must resolve to seeded database records. Use deterministic demo events and seeded data together, or add matching seed records before publishing custom events.

### Worker appears idle

The worker waits for messages and may look idle until the event generator publishes events. Start the worker first, then publish deterministic events from `event-generator/`.

## Git Commit

```bash
git add .
git commit -m "docs add phase 6 worker consumer guide"
```
