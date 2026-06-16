# Phase 7 — Rule-Based Quality Alert Engine

## Goal

Build a deterministic rule-based quality alert engine that runs inside the worker after events are persisted.

## What Was Built

Phase 7 adds rule modules in `worker/app/rules/` and an alert service in `worker/app/services/alert_service.py`.

The worker now evaluates persisted defects, sensor readings, and production events, then creates `quality_alerts` records when a quality risk crosses a threshold. Alerts include structured `evidence_json` so engineers can see why the alert was created.

The phase also adds a deterministic `defect-spike` event-generator mode and a Makefile shortcut:

```powershell
make produce-defect-spike
```

Direct Windows-friendly command:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

## Why This Matters for Manufacturing Quality

Deterministic rules come before AI or machine learning because they are explainable, testable, and easy to validate with manufacturing engineers. A torque reading outside tolerance or five defects at the same station in 30 minutes should generate the same alert every time.

AI can help later with summaries and investigation assistance, but Phase 7 first establishes reliable quality intelligence from known process limits and repeated event patterns.

## Architecture Flow

```text
event-generator -> Redpanda topics -> worker consumers -> PostgreSQL events -> rule engine -> quality_alerts -> quality.alerts topic -> FastAPI read endpoints
```

## Rules Implemented

| Rule | Alert code | Trigger |
| --- | --- | --- |
| Repeated defects at same station | `REPEATED_DEFECT_STATION` | 5 defects at the same station within 30 minutes |
| Equipment temperature high | `EQUIPMENT_TEMPERATURE_HIGH` | `temperature_c` reading above 80 |
| Torque out of tolerance | `TORQUE_OUT_OF_TOLERANCE` | `torque_nm` outside payload limits or fallback 40.0 to 45.0 |
| Vision confidence low | `VISION_CONFIDENCE_LOW` | `vision_confidence` below 0.85 |
| Defect code spike | `DEFECT_CODE_SPIKE` | 5 defects with the same defect code within 30 minutes |
| Consecutive inspection failures | `CONSECUTIVE_INSPECTION_FAILURES` | 3 latest inspection-completed events at a station have failed results |

## Alert Evidence Format

Alerts use the existing `quality_alerts` table:

```text
alert_code
station_id
equipment_id
severity
title
description
evidence_json
status
created_at
```

`evidence_json` stores the facts that caused the alert. Examples include defect counts, time windows, sensor reading IDs, reading values, thresholds, station code, and equipment code.

This evidence supports engineering investigation because the alert does not just say that a problem exists; it records the measurements or defect pattern that crossed the rule threshold.

## Duplicate Alert Prevention

Before creating a new alert, the worker checks for an existing open alert with the same:

- `alert_code`
- `station_id`
- `equipment_id`

If one exists, the new alert is skipped as a duplicate. This prevents the worker from creating the same open alert repeatedly when the same condition is still active or when the same deterministic demo is run again.

## How to Run It

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

### Produce Deterministic Defect Spike

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

### Verify Alerts Through API

```powershell
curl http://localhost:8000/api/v1/alerts
```

### Verify Alerts Topic

```powershell
docker compose exec redpanda rpk topic consume quality.alerts --num 5
```

## Automated Tests

Worker tests cover:

- every rule triggering when the threshold is reached
- every rule staying quiet below threshold
- alert persistence
- duplicate alert prevention
- `quality.alerts` publish calls
- rule-engine execution after event persistence
- invalid or incomplete data not crashing the rule engine

Run:

```powershell
cd worker
pytest
```

Event-generator tests cover the `defect-spike` mode and mock publishing:

```powershell
cd event-generator
pytest
```

Backend tests should still pass:

```powershell
cd backend
pytest
```

## Manual Tests

1. Start PostgreSQL and Redpanda.
2. Run backend migrations.
3. Seed data.
4. Start the API.
5. Create Redpanda topics.
6. Start the worker.
7. Publish deterministic defect-spike events.
8. Verify `/api/v1/alerts`.
9. Verify `quality.alerts` topic messages.
10. Run the same defect spike again and confirm duplicate open alerts are not created.

## Expected Results

- Worker consumes defect and sensor events.
- Worker persists events.
- Rule engine evaluates persisted data.
- At least one alert is created.
- `/api/v1/alerts` returns generated alerts.
- `quality.alerts` receives alert events.
- Running the same defect spike twice does not create duplicate open alerts for the same condition.

## Common Errors and Fixes

### No alerts created because threshold was not reached

Use the deterministic defect spike:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

### Defect spike uses IDs not present in seed data

Run seed data before publishing:

```powershell
cd backend
python -m app.db.seed
```

### Worker not running

Start the worker in its own terminal:

```powershell
cd worker
python -m app.main
```

### Redpanda topic missing

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
```

### quality.alerts topic not created

Run:

```powershell
docker compose exec redpanda rpk topic create quality.alerts
```

### Duplicate alerts appearing repeatedly

Confirm duplicate prevention checks open alerts by `alert_code`, `station_id`, and `equipment_id`. Resolve or acknowledge the existing alert before expecting a new alert for the same condition.

### Alerts created in DB but not visible because API is pointing at wrong database

Confirm `DATABASE_URL` for the worker and backend point to the same PostgreSQL database.

### Sensor payload missing lower_limit or upper_limit

The torque rule uses payload limits when present. If they are missing, it falls back to `40.0` and `45.0`.

## Git Commit

```bash
git add .
git commit -m "phase-7 rule based quality alert engine"
```
