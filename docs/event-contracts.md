# Event Contracts

## Phase 6 Scope

Phase 6 consumes generated manufacturing quality events from Redpanda and persists accepted events to PostgreSQL. It keeps the Phase 5 event contracts and adds worker-side validation, idempotency, and invalid-event logging.

## Base Event Contract

Every generated event follows this base shape:

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "event_timestamp": "iso_datetime",
  "source": "event-generator",
  "plant_id": "uuid",
  "line_id": "uuid",
  "station_id": "uuid",
  "equipment_id": "uuid_or_null",
  "vehicle_id": "uuid_or_null",
  "payload": {}
}
```

## Station Events

Station events describe how a vehicle moves through a manufacturing station.

Supported station event types:

- `station_entered`
- `operation_completed`
- `inspection_completed`
- `station_exited`
- `rework_required`

Example payload fields:

- `station_code`
- `vin`
- `operator_shift`
- `result`
- `cycle_time_seconds`

## Sensor Reading Events

Sensor readings represent measurements from manufacturing equipment.

Supported reading types:

- `torque_nm`
- `temperature_c`
- `vibration_mm_s`
- `pressure_kpa`
- `vision_confidence`

Example payload fields:

- `reading_type`
- `reading_value`
- `unit`
- `equipment_code`
- `lower_limit`
- `upper_limit`

## Defect Events

Defect events represent a detected quality issue.

Supported defect codes:

- `torque_out_of_spec`
- `vision_low_confidence`
- `temperature_excursion`
- `vibration_anomaly`
- `pressure_drop`
- `inspection_failure`

Example payload fields:

- `defect_code`
- `severity`
- `description`
- `measured_value`
- `expected_min`
- `expected_max`

## Deterministic vs Random Events

Deterministic mode prints a fixed sequence of events for repeatable tests and YouTube demos.

Random mode prints the requested number of realistic events with valid UUIDs, ISO timestamps, and values inside manufacturing ranges.

## Topic Routing

| Event type | Topic |
| --- | --- |
| `station_entered` | `station.events` |
| `operation_completed` | `station.events` |
| `inspection_completed` | `station.events` |
| `station_exited` | `station.events` |
| `rework_required` | `station.events` |
| `sensor_reading` | `sensor.readings` |
| `defect_detected` | `quality.defects` |

Additional platform topics are created in Phase 5 so later phases have a stable contract:

- `quality.alerts`
- `investigation.events`

## Producer and Consumer Boundary

The event generator is a producer. It creates events and publishes them to topics.

The worker consumer is separate from FastAPI. FastAPI serves API requests, while the worker runs as a long-lived process that subscribes to topics and writes database rows.

## Phase 6 Persistence Mapping

| Topic | Event type | Table | Important mapping |
| --- | --- | --- | --- |
| `station.events` | Station lifecycle events | `production_events` | `event_id`, `vehicle_id`, `station_id`, `event_type`, `event_timestamp` to `occurred_at`, payload to `payload` |
| `sensor.readings` | `sensor_reading` | `sensor_readings` | `event_id`, `equipment_id`, `station_id`, payload `reading_type`, `reading_value`, `unit`, `event_timestamp` to `recorded_at` |
| `quality.defects` | `defect_detected` | `defects` | `event_id`, payload `defect_code`, `severity`, `description`, `event_timestamp` to `detected_at`, default `status=open` |

The event contract uses UUIDs because real shop-floor systems often use external identifiers. The database currently uses integer primary keys for seeded domain rows. The worker resolves natural keys from payloads first, such as `vin`, `station_code`, and `equipment_code`, then falls back to the deterministic demo UUID suffix convention.

## Idempotency

`event_id` is stored on persisted event rows. Before inserting, the worker checks whether that `event_id` already exists in any ingested event table. If it exists, the event is skipped and logged as `duplicate_event_id`.

This matters because Kafka-compatible systems may redeliver messages during retries, rebalances, or local demo reruns. Idempotency keeps duplicate messages from becoming duplicate production events, sensor readings, or defects.

## Invalid Events

Invalid events are rejected before persistence. Examples include malformed JSON, missing `vehicle_id` on station or defect events, missing `equipment_id` on sensor readings, missing payload fields, unsupported event types, or foreign keys that cannot be resolved.

The worker logs invalid events with a dead-letter placeholder. Full dead-letter topic processing is intentionally left for a later hardening phase.

## Alerts Boundary

Phase 7 generates `quality_alerts` records with deterministic rules. When an alert is created, the worker publishes an alert event to `quality.alerts`.

Alert event payloads include the persisted alert fields:

```json
{
  "id": 1,
  "alert_code": "REPEATED_DEFECT_STATION",
  "station_id": 1,
  "equipment_id": null,
  "severity": "high",
  "title": "Repeated defects detected at A-BODY",
  "description": "5 defects detected at the same station within 30 minutes.",
  "evidence_json": {
    "station_id": 1,
    "station_code": "A-BODY",
    "defect_count": 5,
    "window_minutes": 30
  },
  "status": "open",
  "created_at": "iso_datetime"
}
```

`evidence_json` is the handoff between deterministic rules and engineering investigations. It records the counts, thresholds, readings, station IDs, equipment IDs, and windows that caused the alert.

Frontend dashboard work is intentionally not part of Phase 7. It starts in Phase 8.

## Defect Spike Demo Contract

Phase 7 adds a deterministic event-generator mode:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

The scenario publishes:

- 5 `torque_out_of_spec` defects within 30 minutes
- 1 `torque_nm` reading outside tolerance
- 1 `vision_confidence` reading below threshold

## Manual Commands

```powershell
cd event-generator
pip install -e .
pytest
python -m app.main --mode deterministic
python -m app.main --mode random --count 10
python -m app.main --mode deterministic --publish --broker localhost:19092
python -m app.main --mode random --count 100 --publish --broker localhost:19092
```

If editable install is not available:

```powershell
pip install pydantic pytest kafka-python-ng
```

Write JSON Lines output:

```powershell
python -m app.main --mode deterministic --output events.jsonl
python -m app.main --mode random --count 100 --output events.jsonl
```

Inspect output:

```powershell
Get-Content events.jsonl
```

## Verify Streaming

Start Redpanda:

```powershell
docker compose up redpanda redpanda-console
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Consume events:

```powershell
docker compose exec redpanda rpk topic consume station.events --num 5
docker compose exec redpanda rpk topic consume sensor.readings --num 5
docker compose exec redpanda rpk topic consume quality.defects --num 5
```

## Run the Worker

```powershell
cd worker
pip install -e .
pytest
python -m app.main
```

Useful options:

```powershell
python -m app.main --broker localhost:19092
python -m app.main --topics station.events sensor.readings quality.defects
```
