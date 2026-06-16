from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from app.services.event_mapper import (
    QUALITY_DEFECTS_TOPIC,
    SENSOR_READINGS_TOPIC,
    STATION_EVENTS_TOPIC,
    InvalidEventError,
)
from app.services.persistence import PersistenceError, PersistenceResult

logger = logging.getLogger(__name__)

DEFAULT_TOPICS = (STATION_EVENTS_TOPIC, SENSOR_READINGS_TOPIC, QUALITY_DEFECTS_TOPIC)


@dataclass(frozen=True)
class ConsumerConfig:
    bootstrap_servers: str = "localhost:19092"
    topics: tuple[str, ...] = DEFAULT_TOPICS
    group_id: str = "manufacturing-quality-worker"
    auto_offset_reset: str = "earliest"


class TopicConsumer(Protocol):
    topic: str

    def handle(self, raw_event: str | bytes) -> PersistenceResult:
        pass


def create_kafka_consumer(config: ConsumerConfig):
    try:
        from kafka import KafkaConsumer
    except ImportError as exc:
        raise RuntimeError(
            "kafka-python-ng is required for the worker. Run 'pip install -e .' or "
            "'pip install pydantic sqlalchemy psycopg2-binary kafka-python-ng pytest'."
        ) from exc

    return KafkaConsumer(
        *config.topics,
        bootstrap_servers=config.bootstrap_servers,
        group_id=config.group_id,
        auto_offset_reset=config.auto_offset_reset,
        enable_auto_commit=True,
        value_deserializer=lambda value: value.decode("utf-8"),
    )


def log_dead_letter(topic: str, raw_event: object, error: Exception) -> None:
    logger.warning("Dead-letter placeholder topic=%s reason=%s payload=%r", topic, error, raw_event)


class ConsumerDispatcher:
    def __init__(self, consumers: tuple[TopicConsumer, ...]) -> None:
        self._consumers = {consumer.topic: consumer for consumer in consumers}

    @property
    def topics(self) -> tuple[str, ...]:
        return tuple(self._consumers.keys())

    def process_message(self, topic: str, raw_event: str | bytes) -> PersistenceResult | None:
        consumer = self._consumers.get(topic)

        if consumer is None:
            log_dead_letter(topic, raw_event, InvalidEventError(f"No consumer configured for topic: {topic}"))
            return None

        try:
            result = consumer.handle(raw_event)
        except (InvalidEventError, PersistenceError) as exc:
            log_dead_letter(topic, raw_event, exc)
            return None

        if result.inserted:
            logger.info("Persisted event_id=%s table=%s id=%s", result.event_id, result.table_name, result.record_id)
        else:
            logger.info("Skipped event_id=%s table=%s reason=%s", result.event_id, result.table_name, result.reason)

        return result
