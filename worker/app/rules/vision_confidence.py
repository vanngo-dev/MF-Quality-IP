from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.rules.engine import AlertCandidate, RuleContext
from app.services.persistence import equipment, sensor_readings, stations


class VisionConfidenceRule:
    name = "vision_confidence"

    def __init__(self, threshold: float = 0.85) -> None:
        self.threshold = threshold

    def evaluate(self, session: Session, context: RuleContext | None = None) -> list[AlertCandidate]:
        rows = session.execute(
            select(
                sensor_readings.c.id,
                sensor_readings.c.equipment_id,
                sensor_readings.c.station_id,
                sensor_readings.c.value,
                sensor_readings.c.recorded_at,
                equipment.c.asset_tag,
                equipment.c.station_id.label("equipment_station_id"),
                stations.c.code.label("station_code"),
            )
            .join(equipment, sensor_readings.c.equipment_id == equipment.c.id)
            .join(stations, stations.c.id == sensor_readings.c.station_id)
            .where(
                sensor_readings.c.metric_name == "vision_confidence",
                sensor_readings.c.value < self.threshold,
            )
        ).all()

        candidates: list[AlertCandidate] = []

        for row in rows:
            station_id = row.station_id or row.equipment_station_id

            if station_id is None:
                continue

            candidates.append(
                AlertCandidate(
                    alert_code="VISION_CONFIDENCE_LOW",
                    station_id=int(station_id),
                    equipment_id=int(row.equipment_id),
                    severity="medium",
                    title=f"Low vision confidence at {row.asset_tag}",
                    description=f"Vision confidence {row.value} fell below threshold {self.threshold}.",
                    evidence_json={
                        "sensor_reading_id": int(row.id),
                        "station_id": int(station_id),
                        "station_code": row.station_code,
                        "equipment_id": int(row.equipment_id),
                        "equipment_code": row.asset_tag,
                        "reading_type": "vision_confidence",
                        "reading_value": float(row.value),
                        "threshold": self.threshold,
                        "recorded_at": row.recorded_at.isoformat(),
                    },
                )
            )

        return candidates
