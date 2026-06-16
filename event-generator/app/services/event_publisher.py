from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from app.producers.kafka_producer import EventProducer
from app.schemas.events import BaseEvent

STATION_EVENTS = {
    "station_entered",
    "operation_completed",
    "inspection_completed",
    "station_exited",
    "rework_required",
}
SENSOR_READING_TOPIC = "sensor.readings"
QUALITY_DEFECT_TOPIC = "quality.defects"
STATION_EVENT_TOPIC = "station.events"
DEFAULT_BROKER = "localhost:19092"


@dataclass(frozen=True)
class PublishSummary:
    generated_count: int
    topic_counts: dict[str, int]


def resolve_broker(cli_broker: str | None = None) -> str:
    return cli_broker or os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BROKER


def route_event_to_topic(event: BaseEvent) -> str:
    if event.event_type in STATION_EVENTS:
        return STATION_EVENT_TOPIC

    if event.event_type == "sensor_reading":
        return SENSOR_READING_TOPIC

    if event.event_type == "defect_detected":
        return QUALITY_DEFECT_TOPIC

    raise ValueError(f"Unsupported event_type for topic routing: {event.event_type}")


def serialize_event(event: BaseEvent) -> str:
    validated = BaseEvent.model_validate(event.model_dump())
    return validated.model_dump_json()


def publish_events(events: Iterable[BaseEvent], producer: EventProducer) -> PublishSummary:
    event_list = list(events)
    topic_counter: Counter[str] = Counter()

    for event in event_list:
        topic = route_event_to_topic(event)
        producer.send(topic, serialize_event(event))
        topic_counter[topic] += 1

    producer.flush()

    return PublishSummary(generated_count=len(event_list), topic_counts=dict(topic_counter))


def format_publish_summary(summary: PublishSummary) -> str:
    lines = [f"Generated {summary.generated_count} events."]

    for topic in (STATION_EVENT_TOPIC, SENSOR_READING_TOPIC, QUALITY_DEFECT_TOPIC):
        lines.append(f"Published {summary.topic_counts.get(topic, 0)} events to {topic}.")

    return "\n".join(lines)
