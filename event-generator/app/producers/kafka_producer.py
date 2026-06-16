from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ProducerConfig:
    bootstrap_servers: str = "localhost:19092"


class EventProducer(Protocol):
    def send(self, topic: str, payload: str) -> None:
        pass

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


class KafkaEventProducer:
    def __init__(self, config: ProducerConfig) -> None:
        try:
            from kafka import KafkaProducer
        except ImportError as exc:
            raise RuntimeError(
                "kafka-python-ng is required for publishing. Run 'pip install -e .' or "
                "'pip install pydantic pytest kafka-python-ng'."
            ) from exc

        self._producer = KafkaProducer(
            bootstrap_servers=config.bootstrap_servers,
            value_serializer=lambda value: value.encode("utf-8"),
        )

    def send(self, topic: str, payload: str) -> None:
        self._producer.send(topic, payload)

    def flush(self) -> None:
        self._producer.flush()

    def close(self) -> None:
        self._producer.close()


@dataclass
class InMemoryEventProducer:
    sent_messages: list[tuple[str, str]] = field(default_factory=list)
    was_flushed: bool = False
    was_closed: bool = False

    def send(self, topic: str, payload: str) -> None:
        self.sent_messages.append((topic, payload))

    def flush(self) -> None:
        self.was_flushed = True

    def close(self) -> None:
        self.was_closed = True
