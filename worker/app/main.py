from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass

from app.consumers.base_consumer import ConsumerConfig, ConsumerDispatcher, DEFAULT_TOPICS, create_kafka_consumer
from app.consumers.defect_event_consumer import DefectEventConsumer
from app.consumers.sensor_reading_consumer import SensorReadingConsumer
from app.consumers.station_event_consumer import StationEventConsumer
from app.rules.engine import RuleEngine
from app.services.alert_service import AlertService, KafkaAlertPublisher
from app.services.persistence import PersistenceService, make_session_factory

DEFAULT_BROKER = "localhost:19092"
DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/manufacturing_quality"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorkerConfig:
    broker: str
    database_url: str
    topics: tuple[str, ...]
    group_id: str = "manufacturing-quality-worker"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Consume Redpanda events and persist them to PostgreSQL.")
    parser.add_argument("--broker", help="Kafka bootstrap server. Defaults to KAFKA_BOOTSTRAP_SERVERS or localhost:19092.")
    parser.add_argument("--database-url", help="Database URL. Defaults to DATABASE_URL or the backend local PostgreSQL URL.")
    parser.add_argument("--topics", nargs="+", help="Kafka topics to subscribe to.")
    parser.add_argument("--group-id", default="manufacturing-quality-worker", help="Kafka consumer group id.")
    parser.add_argument("--log-level", default="INFO", help="Python logging level.")

    return parser


def load_config(args: argparse.Namespace) -> WorkerConfig:
    broker = args.broker or os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BROKER
    database_url = args.database_url or os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL
    topics = tuple(args.topics) if args.topics else DEFAULT_TOPICS

    return WorkerConfig(broker=broker, database_url=database_url, topics=topics, group_id=args.group_id)


def build_dispatcher(persistence: PersistenceService, rule_engine: RuleEngine | None = None) -> ConsumerDispatcher:
    return ConsumerDispatcher(
        (
            StationEventConsumer(persistence, rule_engine),
            SensorReadingConsumer(persistence, rule_engine),
            DefectEventConsumer(persistence, rule_engine),
        )
    )


def run_worker(config: WorkerConfig) -> None:
    session_factory = make_session_factory(config.database_url)
    alert_publisher = KafkaAlertPublisher(config.broker)
    alert_service = AlertService(session_factory, alert_publisher)
    rule_engine = RuleEngine(session_factory, alert_service)
    dispatcher = build_dispatcher(PersistenceService(session_factory), rule_engine)
    consumer = create_kafka_consumer(
        ConsumerConfig(
            bootstrap_servers=config.broker,
            topics=config.topics,
            group_id=config.group_id,
        )
    )

    logger.info("Worker connected to broker=%s topics=%s", config.broker, ", ".join(config.topics))

    try:
        for message in consumer:
            dispatcher.process_message(message.topic, message.value)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
    finally:
        consumer.close()
        alert_publisher.close()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO))

    run_worker(load_config(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
