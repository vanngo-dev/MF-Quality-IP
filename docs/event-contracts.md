# Event Contracts

## Phase 4 Scope

Phase 4 generates realistic manufacturing quality events as JSON. It does not publish to Kafka or Redpanda yet. Streaming begins in Phase 5.

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

## Manual Commands

```powershell
cd event-generator
pip install -e .
pytest
python -m app.main --mode deterministic
python -m app.main --mode random --count 10
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
