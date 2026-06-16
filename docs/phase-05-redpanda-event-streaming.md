# Phase 5: Redpanda Event Streaming Producer

## Goal

Connect the Phase 4 event generator to Redpanda/Kafka-compatible event streaming.

## What This Phase Establishes

- Kafka-compatible producer support in `event-generator/`.
- Topic routing for station, sensor, and defect events.
- Redpanda Console in Docker Compose.
- Makefile shortcuts for streaming commands.
- Mock producer tests that do not require Redpanda.

## Broker and Console

Host broker:

```text
localhost:19092
```

Redpanda Console:

```text
http://localhost:8080
```

Container-internal broker:

```text
redpanda:9092
```

## Topics

Phase 5 publishes to:

- `station.events`
- `sensor.readings`
- `quality.defects`

Phase 5 also creates future platform topics:

- `quality.alerts`
- `investigation.events`

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

## Run Redpanda

```powershell
docker compose up redpanda redpanda-console
```

## Create Topics

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

## Publish Events

```powershell
cd event-generator
pip install -e .
pytest
python -m app.main --mode deterministic --publish --broker localhost:19092
python -m app.main --mode random --count 10 --publish --broker localhost:19092
```

If editable install is not available:

```powershell
pip install pydantic pytest kafka-python-ng
```

## Makefile Shortcuts

```powershell
make up-streaming
make create-topics
make produce-demo-events
make produce-random-events
```

On Windows systems without Make, use the direct PowerShell commands above.

## Verify Events

Option 1: Redpanda Console

1. Open http://localhost:8080.
2. Go to Topics.
3. Open `station.events`, `sensor.readings`, and `quality.defects`.
4. Confirm events appear.

Option 2: `rpk`

```powershell
docker compose exec redpanda rpk topic consume station.events --num 5
docker compose exec redpanda rpk topic consume sensor.readings --num 5
docker compose exec redpanda rpk topic consume quality.defects --num 5
```

## What This Phase Does Not Do

- It does not add a worker consumer.
- It does not save streamed events to PostgreSQL.
- It does not add alert rules.
- It does not add frontend code.

## Troubleshooting

- Redpanda container not running: run `docker compose up redpanda redpanda-console`.
- Wrong broker port: use `localhost:19092` from the host.
- Topic does not exist: run the topic creation command.
- Producer dependency issue: install `kafka-python-ng`.
- `confluent-kafka` wheel/build issue on Windows: this project uses `kafka-python-ng`.
- No events visible: confirm you are checking `station.events`, `sensor.readings`, or `quality.defects`.
- Published but not saved: database persistence starts in Phase 6.
