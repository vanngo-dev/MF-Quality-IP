# Architecture

## Current Shape

The project is being built one phase at a time.

```text
frontend/          React + TypeScript user interface
backend/           FastAPI REST API and PostgreSQL domain model
event-generator/   Standalone Python event simulator
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

The worker consumer is intentionally separate. Consumers will be added in Phase 6 so event production can be tested before database persistence or alert rules are introduced.

## Phase 4 Boundary

Phase 4 validates event shape and event generation only. Kafka publishing is intentionally delayed until Phase 5 so the event contract can be tested before streaming infrastructure is added.

## How Phase 4 Prepared Streaming

The generator emits JSON Lines-compatible events with UUIDs and ISO timestamps. Phase 5 reuses these event contracts and adds a Redpanda/Kafka producer without changing the core payload design.

## Phase 5 Boundary

Phase 5 publishes events but does not save them to PostgreSQL. That keeps the streaming contract clear before Phase 6 adds worker consumption and persistence.
