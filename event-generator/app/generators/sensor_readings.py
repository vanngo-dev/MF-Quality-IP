from __future__ import annotations

from datetime import datetime
from random import Random
from uuid import UUID, uuid4

from app.schemas.events import ReadingType, SensorReadingEvent, SensorReadingPayload


SENSOR_SPECS: dict[ReadingType, dict[str, float | str]] = {
    "torque_nm": {"unit": "Nm", "lower_limit": 40.0, "upper_limit": 45.0, "minimum": 35.0, "maximum": 48.0},
    "temperature_c": {"unit": "C", "lower_limit": 18.0, "upper_limit": 85.0, "minimum": 15.0, "maximum": 95.0},
    "vibration_mm_s": {"unit": "mm/s", "lower_limit": 0.0, "upper_limit": 7.5, "minimum": 0.1, "maximum": 12.0},
    "pressure_kpa": {"unit": "kPa", "lower_limit": 280.0, "upper_limit": 360.0, "minimum": 240.0, "maximum": 420.0},
    "vision_confidence": {"unit": "score", "lower_limit": 0.85, "upper_limit": 1.0, "minimum": 0.65, "maximum": 0.99},
}


def build_sensor_reading_event(
    *,
    event_timestamp: datetime,
    plant_id: UUID,
    line_id: UUID,
    station_id: UUID,
    equipment_id: UUID,
    vehicle_id: UUID,
    reading_type: ReadingType,
    reading_value: float,
    equipment_code: str,
    event_id: UUID | None = None,
) -> SensorReadingEvent:
    spec = SENSOR_SPECS[reading_type]
    payload = SensorReadingPayload(
        reading_type=reading_type,
        reading_value=round(reading_value, 3),
        unit=str(spec["unit"]),
        equipment_code=equipment_code,
        lower_limit=float(spec["lower_limit"]),
        upper_limit=float(spec["upper_limit"]),
    )

    return SensorReadingEvent(
        event_id=event_id or uuid4(),
        event_timestamp=event_timestamp,
        plant_id=plant_id,
        line_id=line_id,
        station_id=station_id,
        equipment_id=equipment_id,
        vehicle_id=vehicle_id,
        payload=payload,
    )


def random_sensor_value(reading_type: ReadingType, random: Random) -> float:
    spec = SENSOR_SPECS[reading_type]
    return random.uniform(float(spec["minimum"]), float(spec["maximum"]))
