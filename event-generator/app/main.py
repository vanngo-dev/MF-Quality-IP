from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from app.generators.scenarios import generate_deterministic_events, generate_random_events
from app.producers.kafka_producer import InMemoryEventProducer, KafkaEventProducer, ProducerConfig
from app.schemas.events import BaseEvent
from app.services.event_publisher import format_publish_summary, publish_events, resolve_broker


def event_to_json_line(event: BaseEvent) -> str:
    return event.model_dump_json()


def write_events(events: Iterable[BaseEvent], output: Path | None = None) -> None:
    lines = [event_to_json_line(event) for event in events]

    if output is None:
        for line in lines:
            print(line)
        return

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate simulated manufacturing quality events.")
    parser.add_argument("--mode", choices=["deterministic", "random"], required=True)
    parser.add_argument("--count", type=int, default=10, help="Number of events to generate in random mode.")
    parser.add_argument("--output", type=Path, help="Optional JSON Lines output file.")
    parser.add_argument("--publish", action="store_true", help="Publish generated events to Kafka-compatible topics.")
    parser.add_argument("--broker", help="Kafka bootstrap server. Defaults to KAFKA_BOOTSTRAP_SERVERS or localhost:19092.")
    parser.add_argument("--producer", choices=["kafka", "mock"], default="kafka", help=argparse.SUPPRESS)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be greater than 0")

    if args.mode == "deterministic":
        events = generate_deterministic_events()
    else:
        events = generate_random_events(args.count)

    if args.output is not None:
        write_events(events, args.output)

    if args.publish:
        if args.producer == "mock":
            producer = InMemoryEventProducer()
        else:
            producer = KafkaEventProducer(ProducerConfig(bootstrap_servers=resolve_broker(args.broker)))

        try:
            summary = publish_events(events, producer)
        finally:
            producer.close()

        print(format_publish_summary(summary))
        return 0

    if args.output is None:
        write_events(events)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
