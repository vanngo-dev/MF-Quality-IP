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

## Why Kafka Is Not Used Yet

Phase 4 validates event shape and event generation only. Kafka publishing is intentionally delayed until Phase 5 so the event contract can be tested before streaming infrastructure is added.

## Preparing for Phase 5

The generator already emits JSON Lines-compatible events with UUIDs and ISO timestamps. Phase 5 can reuse these event contracts and add a Redpanda/Kafka producer without changing the core payload design.
