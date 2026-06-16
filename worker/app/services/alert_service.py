from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.services.persistence import quality_alerts, utc_now

logger = logging.getLogger(__name__)

QUALITY_ALERTS_TOPIC = "quality.alerts"


class AlertPublisher(Protocol):
    def publish(self, payload: dict[str, object]) -> None:
        pass

    def close(self) -> None:
        pass


class NullAlertPublisher:
    def publish(self, payload: dict[str, object]) -> None:
        pass

    def close(self) -> None:
        pass


class InMemoryAlertPublisher:
    def __init__(self) -> None:
        self.published: list[dict[str, object]] = []

    def publish(self, payload: dict[str, object]) -> None:
        self.published.append(payload)

    def close(self) -> None:
        pass


class KafkaAlertPublisher:
    def __init__(self, bootstrap_servers: str) -> None:
        try:
            from kafka import KafkaProducer
        except ImportError as exc:
            raise RuntimeError(
                "kafka-python-ng is required for alert publishing. Run 'pip install -e .' or "
                "'pip install pydantic sqlalchemy psycopg2-binary kafka-python-ng pytest'."
            ) from exc

        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
        )

    def publish(self, payload: dict[str, object]) -> None:
        self._producer.send(QUALITY_ALERTS_TOPIC, payload)
        self._producer.flush()

    def close(self) -> None:
        self._producer.close()


@dataclass(frozen=True)
class AlertCreateResult:
    inserted: bool
    alert_code: str
    station_id: int
    equipment_id: int | None
    alert_id: int | None = None
    reason: str | None = None


class AlertService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        publisher: AlertPublisher | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._publisher = publisher or NullAlertPublisher()

    def create_alerts(self, candidates: list[object]) -> list[AlertCreateResult]:
        results: list[AlertCreateResult] = []

        for candidate in candidates:
            results.append(self.create_alert(candidate))

        return results

    def create_alert(self, candidate: object) -> AlertCreateResult:
        with self._session_factory() as session:
            existing = session.scalar(
                select(quality_alerts.c.id).where(
                    quality_alerts.c.alert_code == candidate.alert_code,
                    quality_alerts.c.station_id == candidate.station_id,
                    quality_alerts.c.equipment_id.is_(None)
                    if candidate.equipment_id is None
                    else quality_alerts.c.equipment_id == candidate.equipment_id,
                    quality_alerts.c.status == "open",
                )
            )

            if existing is not None:
                return AlertCreateResult(
                    inserted=False,
                    alert_code=candidate.alert_code,
                    station_id=candidate.station_id,
                    equipment_id=candidate.equipment_id,
                    alert_id=int(existing),
                    reason="duplicate_open_alert",
                )

            values = {
                "alert_code": candidate.alert_code,
                "station_id": candidate.station_id,
                "equipment_id": candidate.equipment_id,
                "severity": candidate.severity,
                "title": candidate.title,
                "description": candidate.description,
                "evidence_json": candidate.evidence_json,
                "status": "open",
                "created_at": utc_now(),
            }
            result = session.execute(quality_alerts.insert().values(**values))
            session.commit()

            alert_id = result.inserted_primary_key[0] if result.inserted_primary_key else None

        payload = values | {"id": alert_id}

        try:
            self._publisher.publish(payload)
        except Exception as exc:
            logger.warning("Created alert_id=%s but could not publish quality.alerts event: %s", alert_id, exc)

        return AlertCreateResult(
            inserted=True,
            alert_code=candidate.alert_code,
            station_id=candidate.station_id,
            equipment_id=candidate.equipment_id,
            alert_id=int(alert_id) if alert_id is not None else None,
        )
