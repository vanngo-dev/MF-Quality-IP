from uuid import UUID

import pytest

from app.generators.scenarios import generate_deterministic_events
from app.schemas.events import BaseEvent
from app.services.event_publisher import (
    QUALITY_DEFECT_TOPIC,
    SENSOR_READING_TOPIC,
    STATION_EVENT_TOPIC,
    resolve_broker,
    route_event_to_topic,
)


def test_topic_routing_sends_station_events_to_station_events() -> None:
    station_event = next(event for event in generate_deterministic_events() if event.event_type == "station_entered")

    assert route_event_to_topic(station_event) == STATION_EVENT_TOPIC


def test_topic_routing_sends_sensor_reading_to_sensor_readings() -> None:
    sensor_event = next(event for event in generate_deterministic_events() if event.event_type == "sensor_reading")

    assert route_event_to_topic(sensor_event) == SENSOR_READING_TOPIC


def test_topic_routing_sends_defect_detected_to_quality_defects() -> None:
    defect_event = next(event for event in generate_deterministic_events() if event.event_type == "defect_detected")

    assert route_event_to_topic(defect_event) == QUALITY_DEFECT_TOPIC


def test_unknown_event_type_fails_clearly() -> None:
    event = BaseEvent(
        event_id=UUID("00000000-0000-0000-0000-000000099999"),
        event_type="unknown_event",
        event_timestamp=generate_deterministic_events()[0].event_timestamp,
        plant_id=UUID("00000000-0000-0000-0000-000000000001"),
        line_id=UUID("00000000-0000-0000-0000-000000000101"),
        station_id=UUID("00000000-0000-0000-0000-000000001001"),
        payload={},
    )

    with pytest.raises(ValueError, match="Unsupported event_type"):
        route_event_to_topic(event)


def test_producer_config_loads_broker_from_cli_or_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")

    assert resolve_broker("localhost:9092") == "localhost:9092"
    assert resolve_broker() == "localhost:19092"

    monkeypatch.delenv("KAFKA_BOOTSTRAP_SERVERS")
    assert resolve_broker() == "localhost:19092"
