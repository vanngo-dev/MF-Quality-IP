# Interview Guide

## 60-Second Project Pitch

I built a full-stack manufacturing quality intelligence platform that simulates factory station events, equipment sensor readings, vehicle defects, quality alerts, and engineering investigations. The system uses FastAPI, PostgreSQL, Redpanda, Elasticsearch, React, and a Python worker to model a realistic internal quality data platform. It includes rule-based alerting, investigation workflows, evidence-grounded AI summaries using a mock provider, automated tests, E2E tests, Docker Compose, and GitHub Actions CI.

## 5-Minute Technical Walkthrough

1. The event generator creates simulated station, sensor, inspection, and defect events.
2. Events are published to Redpanda Kafka-compatible topics.
3. The worker consumes station, sensor, and defect events.
4. The worker validates payloads, maps natural keys to database records, persists data, and skips duplicate event IDs.
5. The rule engine inspects persisted records and creates quality alerts for repeated defects, sensor threshold breaches, defect spikes, and inspection failures.
6. The FastAPI backend exposes plants, lines, stations, equipment, vehicles, defects, alerts, investigations, search, and AI summary endpoints.
7. The React frontend gives quality engineers dashboard, queue, search, alert detail, investigation detail, and AI summary workflows.
8. Elasticsearch supports investigation search across defects, alerts, investigations, and event summaries.
9. The AI summary workflow uses a local mock provider that only summarizes available evidence.
10. Docker Compose, Makefile commands, Playwright E2E, and GitHub Actions CI make the project repeatable.

## System Design Walkthrough

The main design choice is separating event ingestion from request/response APIs.

```text
event-generator -> Redpanda -> worker -> PostgreSQL -> FastAPI -> React
                                               |
                                               -> Elasticsearch search index
```

FastAPI is responsible for serving APIs to the frontend. The worker is responsible for consuming streams, persisting events, and running rules. PostgreSQL is the system of record. Elasticsearch is a derived index for search.

## Architecture Explanation

- `event-generator/`: creates simulated manufacturing events.
- `redpanda`: carries Kafka-compatible event streams.
- `worker/`: consumes topics and applies rule-based alerting.
- `backend/`: FastAPI app and domain APIs.
- `frontend/`: React dashboard and investigation workflow.
- `e2e/`: Playwright workflow tests.
- `.github/workflows/ci.yml`: CI validation.

The FastAPI backend is in `backend/`, not `api/`.

## Database Design Explanation

The schema models a manufacturing quality domain:

- Plants contain production lines.
- Production lines contain stations.
- Stations have equipment.
- Vehicles move through stations.
- Production events capture station activity.
- Sensor readings capture equipment telemetry.
- Defects capture quality failures.
- Quality alerts capture rule-based issues.
- Investigations track engineering follow-up.

PostgreSQL is used because these records are relational, transactional, and need strong references.

## Event Streaming Explanation

Redpanda is used as a Kafka-compatible broker because manufacturing signals naturally arrive as events:

- vehicle enters station;
- equipment reports a sensor reading;
- inspection passes or fails;
- defect is detected.

Topics:

- `station.events`
- `sensor.readings`
- `quality.defects`
- `quality.alerts`
- `investigation.events`

## Worker / Rule Engine Explanation

The worker subscribes to event topics and writes durable facts into PostgreSQL. After persistence, the rule engine checks for quality conditions such as:

- repeated defects at a station;
- equipment temperature over threshold;
- torque out of tolerance;
- low vision confidence;
- same-code defect spikes;
- consecutive inspection failures.

The worker is separate from the API so streaming failures, retries, and long-running consumers do not affect API latency.

## Frontend Explanation

The frontend is a React + TypeScript internal tool. It uses:

- React Router for pages;
- TanStack Query for server state;
- reusable table, badge, loading, error, and detail components;
- workflow pages for alerts and investigations;
- Playwright selectors for stable E2E tests.

The UI is meant for quality engineers reviewing plant status, alerts, evidence, investigations, and search results.

## Search Explanation

PostgreSQL remains the source of truth. Elasticsearch is used for search because engineers need free-text discovery across several record types:

- defects;
- alerts;
- investigations;
- event summaries.

The backend reindex command rebuilds search documents from PostgreSQL:

```powershell
make reindex-search
```

## AI Summary Explanation

The AI summary workflow is intentionally mock-first. It gathers platform evidence from:

- linked alert details;
- alert `evidence_json`;
- related defects;
- related sensor readings;
- related station events;
- investigation notes;
- root-cause hypothesis.

The mock provider produces structured summaries with likely issue, affected station, affected equipment, evidence, recommended checks, confidence, and limitations. It avoids unsupported root-cause claims and does not require paid APIs.

## Testing Strategy Explanation

The project tests multiple layers:

- Backend Pytest API and domain tests.
- Worker tests for mapping, persistence, consumers, and rule engine.
- Event-generator tests for schemas, scenarios, routing, and publishing.
- Frontend Vitest and React Testing Library tests.
- Playwright E2E workflow tests for the alert-to-investigation flow.
- Docker Compose validation.
- GitHub Actions CI for core checks.

E2E tests are local-only in Phase 16 because they require running services and Playwright browsers.

## CI / Docker Explanation

Docker Compose runs local services:

- PostgreSQL;
- Redpanda;
- Redpanda Console;
- Elasticsearch;
- backend;
- worker;
- frontend;
- event generator as a one-shot tools profile.

GitHub Actions runs:

- Docker Compose config validation;
- backend tests;
- worker tests;
- event-generator tests;
- frontend tests and build.

## Tradeoffs

- Simulated events instead of real factory integrations.
- Mock AI provider instead of real LLM calls.
- Minimal auth to keep the project focused on workflow and data platform design.
- Elasticsearch is reindexed by command instead of continuous CDC.
- E2E tests are local-only until CI orchestration is hardened.
- Rule thresholds are deterministic and simple rather than statistically tuned.

## Known Limitations

- Not connected to real factory systems.
- No production authentication or authorization.
- No secrets manager.
- Limited observability.
- No deployment manifests beyond Docker Compose.
- Mock AI provider is not a substitute for a real model evaluation workflow.
- Screenshots are not committed yet.

## What I Would Improve With More Time

- Authentication and role-based access control.
- Real Kafka deployment profiles.
- Richer event schemas.
- Better Elasticsearch mappings.
- Observability with OpenTelemetry.
- Production-grade alert deduplication.
- Historical trend analytics.
- Model/provider abstraction for real LLMs.
- More robust E2E fixtures.
- Kubernetes deployment.

## Resume Bullets

- Built a full-stack Manufacturing Quality Intelligence Platform using FastAPI, React, PostgreSQL, Redpanda, Elasticsearch, and Docker Compose to simulate factory quality event ingestion, alerting, investigation, and search workflows.
- Implemented event-driven ingestion pipeline with Kafka-compatible Redpanda topics, Python worker consumers, SQLAlchemy persistence, and rule-based quality alert generation for simulated station, sensor, and defect events.
- Designed investigation workflow with evidence-based alerts, Elasticsearch search, and mock AI-assisted root-cause summaries constrained to real event data and documented limitations.
- Added automated backend, worker, event-generator, frontend, E2E, and GitHub Actions CI tests to demonstrate production-oriented engineering practices.

## Likely Interview Questions and Answers

### Why did you choose Redpanda?

Redpanda is Kafka-compatible and easy to run locally with Docker Compose. It lets the project model event-driven factory ingestion without requiring a heavier Kafka/Zookeeper setup.

### Why separate the worker from the API?

The API should stay responsive for request/response traffic. The worker handles long-running stream consumption, retries, idempotency, persistence, and rule execution without affecting API latency.

### Why PostgreSQL and Elasticsearch?

PostgreSQL is the source of truth for relational manufacturing records. Elasticsearch is a derived index optimized for free-text search across defects, alerts, investigations, and event summaries.

### How does idempotency work?

Persisted event rows store `event_id`. Before inserting, the worker checks whether that event ID already exists and skips duplicates safely.

### How do you prevent duplicate alerts?

The alert service checks for existing open alerts with the same alert code, station, and equipment before creating a new alert.

### How do you prevent AI hallucination?

The default provider is a deterministic mock provider. It only summarizes platform evidence, includes limitations, uses cautious language, and does not call external APIs.

### How would you scale this system?

I would scale workers horizontally by consumer group, partition topics by plant or station, tune database indexes, isolate Elasticsearch indexing, and add observability around lag, throughput, and failed events.

### How would you secure this system?

I would add authentication, role-based access control, secrets management, audit logs, API authorization checks, container hardening, and network policies.

### How would you deploy this in production?

I would use managed PostgreSQL, managed Kafka or Redpanda, managed Elasticsearch or OpenSearch, containerized backend and worker services, CI/CD, infrastructure as code, observability, and environment-specific secrets.

### What tradeoffs did you make?

I optimized for clear portfolio demonstration: simulated data, deterministic rules, mock AI, local Docker Compose, and tests. I intentionally deferred production auth, observability, and Kubernetes.
