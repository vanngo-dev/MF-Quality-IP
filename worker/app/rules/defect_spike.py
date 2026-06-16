from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.rules.engine import AlertCandidate, RuleContext
from app.services.persistence import defects, stations


class DefectSpikeRule:
    name = "defect_spike"

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
                defects.c.defect_code,
                defect_count.label("defect_count"),
            )
            .join(stations, defects.c.station_id == stations.c.id)
            .where(defects.c.detected_at >= window_start)
            .group_by(defects.c.station_id, stations.c.code, defects.c.defect_code)
            .having(defect_count >= self.threshold)
        ).all()

        return [
            AlertCandidate(
                alert_code="DEFECT_CODE_SPIKE",
                station_id=int(row.station_id),
                equipment_id=None,
                severity="high",
                title=f"Defect spike detected for {row.defect_code}",
                description=(
                    f"{row.defect_count} defects with code {row.defect_code} were detected within "
                    f"{self.window_minutes} minutes."
                ),
                evidence_json={
                    "station_id": int(row.station_id),
                    "station_code": row.station_code,
                    "defect_code": row.defect_code,
                    "defect_count": int(row.defect_count),
                    "window_minutes": self.window_minutes,
                },
            )
            for row in rows
        ]
