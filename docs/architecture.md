# Architecture

## Current Shape

The project is being built one phase at a time.

```text
frontend/          React + TypeScript user interface
backend/           FastAPI REST API and PostgreSQL domain model
event-generator/   Standalone Python event simulator
worker/            Standalone Python Kafka consumer and database ingestion worker
docker-compose.yml Local PostgreSQL, Redpanda, and Elasticsearch services
```

## Phase 4 Event Generator

The event generator simulates manufacturing data without depending on the backend, PostgreSQL, Redpanda, or Elasticsearch.

It generates:

- Station lifecycle events.
- Equipment sensor readings.
- Inspection events.
- Defect events.

## Why Simulated Data Is Useful

Simulated data lets the project demonstrate realistic manufacturing behavior before real shop-floor integrations exist. It also supports repeatable tests, demos, and future streaming work.

## Deterministic and Random Modes

Deterministic mode produces a fixed event sequence. Use it for tests and recorded demos.

Random mode produces a requested number of realistic events. Use it to show variety during local development.

## Phase 5 Redpanda Streaming

Redpanda provides a Kafka-compatible event streaming layer for local development.

Kafka-style streaming fits manufacturing systems because shop-floor activity is naturally event-driven: vehicles enter stations, tools report readings, inspections finish, and defects are detected over time.

The Phase 5 event generator publishes to these topics:

- `station.events`
- `sensor.readings`
- `quality.defects`

It also creates these future workflow topics:

- `quality.alerts`
- `investigation.events`

## Producer and Consumer Separation

The event generator is the producer. It sends events to Redpanda.

The worker consumer is intentionally separate from the FastAPI application. FastAPI handles request/response APIs. The worker handles long-running topic consumption and persistence so API latency, consumer retries, and streaming failures do not get tangled together.

## Phase 4 Boundary

Phase 4 validates event shape and event generation only. Kafka publishing is intentionally delayed until Phase 5 so the event contract can be tested before streaming infrastructure is added.

## How Phase 4 Prepared Streaming

The generator emits JSON Lines-compatible events with UUIDs and ISO timestamps. Phase 5 reuses these event contracts and adds a Redpanda/Kafka producer without changing the core payload design.

## Phase 5 Boundary

Phase 5 publishes events but does not save them to PostgreSQL. That keeps the streaming contract clear before Phase 6 adds worker consumption and persistence.

## Phase 6 Worker Consumers

Phase 6 adds a Python worker in `worker/`. It subscribes to the three producer topics from Phase 5:

- `station.events`
- `sensor.readings`
- `quality.defects`

The worker validates each event envelope, maps the payload to persistence data, resolves the referenced vehicle, station, and equipment rows, and writes to PostgreSQL.

See `docs/phase6.md` for the Phase 6 worker runbook and troubleshooting guide.

## Topic to Table Mapping

| Topic | Persisted table |
| --- | --- |
| `station.events` | `production_events` |
| `sensor.readings` | `sensor_readings` |
| `quality.defects` | `defects` |

The worker stores `event_id` on persisted event rows and checks that ID before inserting. This makes ingestion idempotent: if Redpanda redelivers an event or the generator publishes the same deterministic event twice, the worker logs a duplicate skip instead of creating another row.

Invalid events are logged through a dead-letter placeholder. Phase 6 does not build a full dead-letter replay workflow; it only prevents malformed or unresolvable messages from crashing the worker.

## Phase 6 Boundary

Phase 6 persists production events, sensor readings, and defects. It does not generate `quality_alerts`, run rule-based alert logic, add frontend screens, add Elasticsearch indexing, or create AI summaries. Alert rules start in Phase 7.

## Phase 7 Rule-Based Alert Engine

Phase 7 adds deterministic quality intelligence inside the worker. After the worker persists a new defect, sensor reading, or production event, it runs a rule engine against persisted data and creates `quality_alerts` records when thresholds are met.

The Phase 7 flow is:

```text
event-generator -> Redpanda topics -> worker consumers -> PostgreSQL events -> rule engine -> quality_alerts -> quality.alerts topic -> FastAPI read endpoints
```

Rules are deterministic and evidence-based. They cover repeated defects at the same station, high equipment temperature, torque readings outside tolerance, low vision confidence, defect-code spikes, and consecutive inspection failures.

Duplicate open alerts are prevented by checking for an existing open alert with the same `alert_code`, `station_id`, and `equipment_id`. Alert payloads are also published to `quality.alerts` when an alert is created.

See `docs/phase7.md` for the Phase 7 runbook and troubleshooting guide.

## Phase 7 Boundary

Phase 7 does not add frontend dashboard work, Elasticsearch indexing, AI summaries, or machine learning. Frontend dashboard work starts in Phase 8.
