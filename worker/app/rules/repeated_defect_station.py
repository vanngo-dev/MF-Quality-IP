from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.rules.engine import AlertCandidate, RuleContext
from app.services.persistence import defects, stations


class RepeatedDefectStationRule:
    name = "repeated_defect_station"

    def __init__(self, threshold: int = 5, window_minutes: int = 30) -> None:
        self.threshold = threshold
        self.window_minutes = window_minutes

    def evaluate(self, session: Session, context: RuleContext | None = None) -> list[AlertCandidate]:
        latest_detected_at = session.scalar(select(func.max(defects.c.detected_at)))

        if latest_detected_at is None:
            return []

        window_start = latest_detected_at - timedelta(minutes=self.window_minutes)
        defect_count = func.count(defects.c.id)
        rows = session.execute(
            select(
                defects.c.station_id,
                stations.c.code.label("station_code"),
                defect_count.label("defect_count"),
            )
            .join(stations, defects.c.station_id == stations.c.id)
            .where(defects.c.detected_at >= window_start)
            .group_by(defects.c.station_id, stations.c.code)
            .having(defect_count >= self.threshold)
        ).all()

        return [
            AlertCandidate(
                alert_code="REPEATED_DEFECT_STATION",
                station_id=int(row.station_id),
                equipment_id=None,
                severity="high",
                title=f"Repeated defects detected at {row.station_code}",
                description=f"{row.defect_count} defects detected at the same station within {self.window_minutes} minutes.",
                evidence_json={
                    "station_id": int(row.station_id),
                    "station_code": row.station_code,
                    "defect_count": int(row.defect_count),
                    "window_minutes": self.window_minutes,
                },
            )
            for row in rows
        ]
