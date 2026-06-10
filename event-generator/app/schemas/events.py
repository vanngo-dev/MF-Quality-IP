from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

StationEventType = Literal[
    "station_entered",
    "operation_completed",
    "inspection_completed",
    "station_exited",
    "rework_required",
]
ReadingType = Literal["torque_nm", "temperature_c", "vibration_mm_s", "pressure_kpa", "vision_confidence"]
DefectCode = Literal[
    "torque_out_of_spec",
    "vision_low_confidence",
    "temperature_excursion",
    "vibration_anomaly",
    "pressure_drop",
    "inspection_failure",
]
DefectSeverity = Literal["low", "medium", "high", "critical"]


class BaseEvent(BaseModel):
    event_id: UUID
    event_type: str
    event_timestamp: datetime
    source: Literal["event-generator"] = "event-generator"
    plant_id: UUID
    line_id: UUID
    station_id: UUID
    equipment_id: UUID | None = None
    vehicle_id: UUID | None = None
    payload: dict[str, Any]


class StationPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    station_code: str
    vin: str
    operator_shift: str
    result: str | None = None
    cycle_time_seconds: Annotated[float | None, Field(ge=0)] = None


class StationEvent(BaseEvent):
    event_type: StationEventType
    vehicle_id: UUID
    payload: StationPayload


class SensorReadingPayload(BaseModel):
    reading_type: ReadingType
    reading_value: float
    unit: str
    equipment_code: str
    lower_limit: float
    upper_limit: float

    @model_validator(mode="after")
    def validate_realistic_value(self) -> SensorReadingPayload:
        ranges = {
            "torque_nm": (0.0, 100.0),
            "temperature_c": (-20.0, 150.0),
            "vibration_mm_s": (0.0, 50.0),
            "pressure_kpa": (0.0, 1000.0),
            "vision_confidence": (0.0, 1.0),
        }
        minimum, maximum = ranges[self.reading_type]

        if not minimum <= self.reading_value <= maximum:
            raise ValueError(f"{self.reading_type} reading_value must be between {minimum} and {maximum}")

        if self.lower_limit > self.upper_limit:
            raise ValueError("lower_limit must be less than or equal to upper_limit")

        return self


class SensorReadingEvent(BaseEvent):
    event_type: Literal["sensor_reading"] = "sensor_reading"
    equipment_id: UUID
    vehicle_id: UUID
    payload: SensorReadingPayload


class DefectPayload(BaseModel):
    defect_code: DefectCode
    severity: DefectSeverity
    description: str
    measured_value: float
    expected_min: float
    expected_max: float

    @model_validator(mode="after")
    def validate_expected_range(self) -> DefectPayload:
        if self.expected_min > self.expected_max:
            raise ValueError("expected_min must be less than or equal to expected_max")

        return self


class DefectEvent(BaseEvent):
    event_type: Literal["defect_detected"] = "defect_detected"
    vehicle_id: UUID
    payload: DefectPayload
