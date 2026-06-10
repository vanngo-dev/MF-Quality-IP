import json
import subprocess
import sys

from app.generators.scenarios import generate_deterministic_events
from app.main import event_to_json_line
from app.schemas.events import BaseEvent


def test_deterministic_generation_returns_expected_number_of_events() -> None:
    events = generate_deterministic_events()

    assert len(events) == 6


def test_deterministic_generation_includes_station_sensor_inspection_and_defect_events() -> None:
    event_types = [event.event_type for event in generate_deterministic_events()]

    assert "station_entered" in event_types
    assert "operation_completed" in event_types
    assert "sensor_reading" in event_types
    assert "inspection_completed" in event_types
    assert "defect_detected" in event_types
    assert "station_exited" in event_types


def test_deterministic_generation_serializes_to_valid_json_events() -> None:
    lines = [event_to_json_line(event) for event in generate_deterministic_events()]

    for line in lines:
        BaseEvent.model_validate(json.loads(line))


def test_cli_deterministic_mode_exits_successfully() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.main", "--mode", "deterministic"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert len(result.stdout.strip().splitlines()) == 6
