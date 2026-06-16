from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.rules.engine import AlertCandidate, RuleContext
from app.services.persistence import production_events, stations


class ConsecutiveInspectionFailuresRule:
    name = "consecutive_inspection_failures"

    def __init__(self, threshold: int = 3) -> None:
        self.threshold = threshold

    def evaluate(self, session: Session, context: RuleContext | None = None) -> list[AlertCandidate]:
        rows = session.execute(
            select(
                production_events.c.id,
                production_events.c.station_id,
                production_events.c.payload,
                production_events.c.occurred_at,
                stations.c.code.label("station_code"),
            )
            .join(stations, production_events.c.station_id == stations.c.id)
            .where(production_events.c.event_type == "inspection_completed")
            .order_by(production_events.c.station_id, production_events.c.occurred_at.desc(), production_events.c.id.desc())
        ).all()

        by_station: dict[int, list[object]] = defaultdict(list)

        for row in rows:
            if len(by_station[int(row.station_id)]) < self.threshold:
                by_station[int(row.station_id)].append(row)

        candidates: list[AlertCandidate] = []

        for station_id, station_rows in by_station.items():
            if len(station_rows) < self.threshold:
                continue

            if not all(_is_failed(row.payload) for row in station_rows):
                continue

            latest = station_rows[0]
            candidates.append(
                AlertCandidate(
                    alert_code="CONSECUTIVE_INSPECTION_FAILURES",
                    station_id=station_id,
                    equipment_id=None,
                    severity="high",
                    title=f"Consecutive inspection failures at {latest.station_code}",
                    description=f"{self.threshold} consecutive inspection failures detected at the same station.",
                    evidence_json={
                        "station_id": station_id,
                        "station_code": latest.station_code,
                        "failure_count": self.threshold,
                        "event_ids": [int(row.id) for row in station_rows],
                        "latest_failure_at": latest.occurred_at.isoformat(),
                    },
                )
            )

        return candidates


def _is_failed(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False

    return str(payload.get("result", "")).lower() in {"fail", "failed", "inspection_failed"}
