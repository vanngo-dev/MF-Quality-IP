from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.rules.engine import AlertCandidate, RuleContext
from app.services.event_mapper import SensorReadingData
from app.services.persistence import equipment, sensor_readings, stations


class TorqueOutOfToleranceRule:
    name = "torque_out_of_tolerance"

    def __init__(self, lower_limit: float = 40.0, upper_limit: float = 45.0) -> None:
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def evaluate(self, session: Session, context: RuleContext | None = None) -> list[AlertCandidate]:
        if (
            context is not None
            and isinstance(context.event_data, SensorReadingData)
            and context.event_data.reading_type == "torque_nm"
            and context.persistence_result.table_name == "sensor_readings"
            and context.persistence_result.record_id is not None
        ):
            lower_limit = context.event_data.lower_limit if context.event_data.lower_limit is not None else self.lower_limit
            upper_limit = context.event_data.upper_limit if context.event_data.upper_limit is not None else self.upper_limit
            rows = self._rows(session, context.persistence_result.record_id)
        else:
            lower_limit = self.lower_limit
            upper_limit = self.upper_limit
            rows = self._rows(session)

        return [
            self._candidate(row, lower_limit, upper_limit)
            for row in rows
            if row.value < lower_limit or row.value > upper_limit
        ]

    def _rows(self, session: Session, reading_id: int | None = None) -> list[object]:
        query = (
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
            .where(sensor_readings.c.metric_name == "torque_nm")
        )

        if reading_id is not None:
            query = query.where(sensor_readings.c.id == reading_id)

        return list(session.execute(query).all())

    def _candidate(self, row: object, lower_limit: float, upper_limit: float) -> AlertCandidate:
        station_id = row.station_id or row.equipment_station_id
        direction = "below" if row.value < lower_limit else "above"
        limit = lower_limit if row.value < lower_limit else upper_limit

        return AlertCandidate(
            alert_code="TORQUE_OUT_OF_TOLERANCE",
            station_id=int(station_id),
            equipment_id=int(row.equipment_id),
            severity="high",
            title=f"Torque reading out of tolerance at {row.asset_tag}",
            description=f"Torque reading {row.value} Nm was {direction} tolerance limit {limit} Nm.",
            evidence_json={
                "sensor_reading_id": int(row.id),
                "station_id": int(station_id),
                "station_code": row.station_code,
                "equipment_id": int(row.equipment_id),
                "equipment_code": row.asset_tag,
                "reading_type": "torque_nm",
                "reading_value": float(row.value),
                "lower_limit": lower_limit,
                "upper_limit": upper_limit,
                "recorded_at": row.recorded_at.isoformat(),
            },
        )
