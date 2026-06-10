# Phase 4: Simulated Manufacturing Event Generator

## Goal

Create a standalone Python event generator that simulates manufacturing station events, equipment sensor readings, inspection events, and defect events.

## What This Phase Establishes

- Pydantic event schemas.
- Deterministic event generation for repeatable tests and demos.
- Random event generation for realistic local data.
- Optional JSON Lines file output.
- Tests for schema validation, deterministic generation, random generation, and CLI behavior.

## What This Phase Does Not Do

- It does not publish to Kafka or Redpanda.
- It does not connect to PostgreSQL.
- It does not add a worker consumer.
- It does not add frontend code.

## Run It

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

## Optional JSON Lines Output

```powershell
python -m app.main --mode deterministic --output events.jsonl
python -m app.main --mode random --count 100 --output events.jsonl
Get-Content events.jsonl
```

## Expected Results

- Deterministic mode prints six stable JSON events.
- Random mode prints the requested number of JSON events.
- Event timestamps are ISO datetimes.
- IDs are valid UUIDs.
- Sensor readings stay inside realistic manufacturing ranges.

## Troubleshooting

- `ModuleNotFoundError: pydantic`: run `pip install -e .` or `pip install pydantic pytest`.
- `No module named app.main`: run the command from inside `event-generator`.
- JSON serialization issues: use the CLI output or `model_dump_json()` so UUIDs and datetimes serialize correctly.
- Invalid event count: pass a positive value to `--count`.
- Kafka confusion: Phase 4 only prints events; Kafka publishing starts in Phase 5.
