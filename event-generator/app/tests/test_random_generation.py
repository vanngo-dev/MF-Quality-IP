import json
import subprocess
import sys

import pytest

from app.generators.scenarios import generate_random_events
from app.main import event_to_json_line
from app.schemas.events import BaseEvent


def test_random_generation_respects_requested_count() -> None:
    events = generate_random_events(10, seed=42)

    assert len(events) == 10


def test_random_generation_produces_valid_event_schemas() -> None:
    for event in generate_random_events(25, seed=7):
        BaseEvent.model_validate(json.loads(event_to_json_line(event)))


def test_invalid_random_count_fails_gracefully() -> None:
    with pytest.raises(ValueError, match="count must be greater than 0"):
        generate_random_events(0)


def test_cli_random_mode_exits_successfully() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.main", "--mode", "random", "--count", "10"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert len(result.stdout.strip().splitlines()) == 10


def test_cli_invalid_random_count_exits_with_error() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.main", "--mode", "random", "--count", "0"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "--count must be greater than 0" in result.stderr
