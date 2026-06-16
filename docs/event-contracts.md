# Event Contracts

## Phase 5 Scope

Phase 5 publishes generated manufacturing quality events to Redpanda using Kafka-compatible producer APIs. It does not consume events or persist them to PostgreSQL yet.

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

The worker consumer is intentionally not built in Phase 5. Phase 6 will consume events and decide how to persist or process them.

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
pip install pydantic pytest
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
