from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from app.consumers.base_consumer import ConsumerConfig, DEFAULT_TOPICS, ConsumerDispatcher, create_kafka_consumer
from app.main import DEFAULT_BROKER, DEFAULT_DATABASE_URL, build_parser, load_config
from app.services.event_mapper import (
    QUALITY_DEFECTS_TOPIC,
    SENSOR_READINGS_TOPIC,
    STATION_EVENTS_TOPIC,
    InvalidEventError,
    map_defect_event,
    map_sensor_reading_event,
    map_station_event,
)
from app.services.persistence import PersistenceResult


def _base_event() -> dict[str, object]:
    return {
        "event_id": "00000000-0000-0000-0000-000000000001",
        "event_type": "station_entered",
        "event_timestamp": "2026-01-01T08:00:00Z",
        "source": "event-generator",
        "plant_id": "00000000-0000-0000-0000-000000000001",
        "line_id": "00000000-0000-0000-0000-000000000101",
        "station_id": "00000000-0000-0000-0000-000000000001",
        "equipment_id": None,
        "vehicle_id": "00000000-0000-0000-0000-000000000001",
        "payload": {},
    }


def test_invalid_station_event_is_rejected() -> None:
    event = _base_event()
    event["vehicle_id"] = None

    with pytest.raises(InvalidEventError, match="vehicle_id"):
        map_station_event(event)


def test_invalid_sensor_reading_event_is_rejected() -> None:
    event = _base_event() | {
        "event_type": "sensor_reading",
        "equipment_id": "00000000-0000-0000-0000-000000000001",
        "payload": {"reading_value": 42.7, "unit": "Nm"},
    }

    with pytest.raises(InvalidEventError, match="reading_type"):
        map_sensor_reading_event(event)


def test_invalid_defect_event_is_rejected() -> None:
    event = _base_event() | {
        "event_type": "defect_detected",
        "payload": {"severity": "high", "description": "Missing defect code"},
    }

    with pytest.raises(InvalidEventError, match="defect_code"):
        map_defect_event(event)


def test_worker_configuration_loads_broker_and_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    args = build_parser().parse_args([])

    config = load_config(args)

    assert config.broker == "localhost:29092"
    assert config.database_url == "sqlite+pysqlite:///:memory:"
    assert config.topics == DEFAULT_TOPICS


def test_worker_configuration_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KAFKA_BOOTSTRAP_SERVERS", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    args = build_parser().parse_args([])

    config = load_config(args)

    assert config.broker == DEFAULT_BROKER
    assert config.database_url == DEFAULT_DATABASE_URL


def test_consumer_topic_subscription_configuration_is_correct() -> None:
    assert ConsumerConfig().topics == (STATION_EVENTS_TOPIC, SENSOR_READINGS_TOPIC, QUALITY_DEFECTS_TOPIC)


def test_kafka_consumer_receives_configured_topics(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    class FakeKafkaConsumer:
        def __init__(self, *topics: str, **kwargs: object) -> None:
            calls["topics"] = topics
            calls["kwargs"] = kwargs

    monkeypatch.setitem(sys.modules, "kafka", SimpleNamespace(KafkaConsumer=FakeKafkaConsumer))

    create_kafka_consumer(ConsumerConfig(bootstrap_servers="localhost:19092"))

    assert calls["topics"] == DEFAULT_TOPICS
    assert calls["kwargs"]["bootstrap_servers"] == "localhost:19092"
    assert calls["kwargs"]["group_id"] == "manufacturing-quality-worker"


def test_dispatcher_logs_invalid_events_without_crashing(caplog: pytest.LogCaptureFixture) -> None:
    class FailingConsumer:
        topic = STATION_EVENTS_TOPIC

        def handle(self, raw_event: str | bytes) -> PersistenceResult:
            raise InvalidEventError("bad payload")

    dispatcher = ConsumerDispatcher((FailingConsumer(),))

    result = dispatcher.process_message(STATION_EVENTS_TOPIC, "{}")

    assert result is None
    assert "Dead-letter placeholder" in caplog.text
