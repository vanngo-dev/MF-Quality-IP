import json

from app.generators.scenarios import generate_deterministic_events
from app.producers.kafka_producer import InMemoryEventProducer
from app.services.event_publisher import (
    QUALITY_DEFECT_TOPIC,
    SENSOR_READING_TOPIC,
    STATION_EVENT_TOPIC,
    publish_events,
)


def test_mock_producer_receives_expected_topic_and_payload() -> None:
    producer = InMemoryEventProducer()
    events = generate_deterministic_events()

    summary = publish_events(events, producer)

    assert summary.generated_count == 6
    assert summary.topic_counts == {
        STATION_EVENT_TOPIC: 4,
        SENSOR_READING_TOPIC: 1,
        QUALITY_DEFECT_TOPIC: 1,
    }
    assert producer.was_flushed is True
    assert producer.sent_messages[0][0] == STATION_EVENT_TOPIC
    assert json.loads(producer.sent_messages[0][1])["event_type"] == "station_entered"


def test_publish_mode_validates_event_before_publishing() -> None:
    producer = InMemoryEventProducer()

    publish_events(generate_deterministic_events(), producer)

    for _, payload in producer.sent_messages:
        body = json.loads(payload)
        assert body["event_id"]
        assert body["event_timestamp"]
        assert body["source"] == "event-generator"
