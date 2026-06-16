from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError

STATION_EVENTS_TOPIC = "station.events"
SENSOR_READINGS_TOPIC = "sensor.readings"
QUALITY_DEFECTS_TOPIC = "quality.defects"

STATION_EVENT_TYPES = {
    "station_entered",
    "operation_completed",
    "inspection_completed",
    "station_exited",
    "rework_required",
}


class InvalidEventError(ValueError):
    """Raised when a streamed event cannot be safely persisted."""


class BaseEventEnvelope(BaseModel):
    event_id: UUID
    event_type: str
    event_timestamp: datetime
    source: str = "event-generator"
    plant_id: UUID
    line_id: UUID
    station_id: UUID
    equipment_id: UUID | None = None
    vehicle_id: UUID | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


@dataclass(frozen=True)
class ProductionEventData:
    event_id: str
    vehicle_external_id: str
    station_external_id: str
    event_type: str
    event_timestamp: datetime
    payload_json: dict[str, Any]
    vin: str | None = None
    station_code: str | None = None


@dataclass(frozen=True)
class SensorReadingData:
    event_id: str
    equipment_external_id: str
    station_external_id: str
    reading_type: str
    reading_value: float
    unit: str
    reading_timestamp: datetime
    equipment_code: str | None = None
    station_code: str | None = None


@dataclass(frozen=True)
class DefectData:
    event_id: str
    defect_code: str
    vehicle_external_id: str
    station_external_id: str
    equipment_external_id: str | None
    severity: str
    description: str
    detected_at: datetime
    status: str = "open"
    vin: str | None = None
    station_code: str | None = None
    equipment_code: str | None = None


def _load_raw_event(raw_event: str | bytes | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(raw_event, bytes):
        raw_event = raw_event.decode("utf-8")

    if isinstance(raw_event, str):
        try:
            loaded = json.loads(raw_event)
        except json.JSONDecodeError as exc:
            raise InvalidEventError(f"Event payload is not valid JSON: {exc.msg}") from exc

        if not isinstance(loaded, dict):
            raise InvalidEventError("Event payload must be a JSON object.")

        return loaded

    return dict(raw_event)


def _validate_envelope(raw_event: str | bytes | Mapping[str, Any]) -> BaseEventEnvelope:
    try:
        return BaseEventEnvelope.model_validate(_load_raw_event(raw_event))
    except ValidationError as exc:
        raise InvalidEventError(str(exc)) from exc


def _required_payload_value(payload: Mapping[str, Any], field_name: str) -> Any:
    value = payload.get(field_name)

    if value is None or value == "":
        raise InvalidEventError(f"Missing required payload field: {field_name}")

    return value


def _optional_payload_string(payload: Mapping[str, Any], field_name: str) -> str | None:
    value = payload.get(field_name)

    if value is None or value == "":
        return None

    return str(value)


def map_station_event(raw_event: str | bytes | Mapping[str, Any]) -> ProductionEventData:
    event = _validate_envelope(raw_event)

    if event.event_type not in STATION_EVENT_TYPES:
        raise InvalidEventError(f"Unsupported station event_type: {event.event_type}")

    if event.vehicle_id is None:
        raise InvalidEventError("Station events require vehicle_id.")

    return ProductionEventData(
        event_id=str(event.event_id),
        vehicle_external_id=str(event.vehicle_id),
        station_external_id=str(event.station_id),
        event_type=event.event_type,
        event_timestamp=event.event_timestamp,
        payload_json=event.payload,
        vin=_optional_payload_string(event.payload, "vin"),
        station_code=_optional_payload_string(event.payload, "station_code"),
    )


def map_sensor_reading_event(raw_event: str | bytes | Mapping[str, Any]) -> SensorReadingData:
    event = _validate_envelope(raw_event)

    if event.event_type != "sensor_reading":
        raise InvalidEventError(f"Unsupported sensor reading event_type: {event.event_type}")

    if event.equipment_id is None:
        raise InvalidEventError("Sensor reading events require equipment_id.")

    reading_value = _required_payload_value(event.payload, "reading_value")

    try:
        numeric_value = float(reading_value)
    except (TypeError, ValueError) as exc:
        raise InvalidEventError("payload.reading_value must be numeric.") from exc

    return SensorReadingData(
        event_id=str(event.event_id),
        equipment_external_id=str(event.equipment_id),
        station_external_id=str(event.station_id),
        reading_type=str(_required_payload_value(event.payload, "reading_type")),
        reading_value=numeric_value,
        unit=str(_required_payload_value(event.payload, "unit")),
        reading_timestamp=event.event_timestamp,
        equipment_code=_optional_payload_string(event.payload, "equipment_code"),
        station_code=_optional_payload_string(event.payload, "station_code"),
    )


def map_defect_event(raw_event: str | bytes | Mapping[str, Any]) -> DefectData:
    event = _validate_envelope(raw_event)

    if event.event_type != "defect_detected":
        raise InvalidEventError(f"Unsupported defect event_type: {event.event_type}")

    if event.vehicle_id is None:
        raise InvalidEventError("Defect events require vehicle_id.")

    return DefectData(
        event_id=str(event.event_id),
        defect_code=str(_required_payload_value(event.payload, "defect_code")),
        vehicle_external_id=str(event.vehicle_id),
        station_external_id=str(event.station_id),
        equipment_external_id=str(event.equipment_id) if event.equipment_id is not None else None,
        severity=str(_required_payload_value(event.payload, "severity")),
        description=str(_required_payload_value(event.payload, "description")),
        detected_at=event.event_timestamp,
        vin=_optional_payload_string(event.payload, "vin"),
        station_code=_optional_payload_string(event.payload, "station_code"),
        equipment_code=_optional_payload_string(event.payload, "equipment_code"),
    )


def map_event_for_topic(topic: str, raw_event: str | bytes | Mapping[str, Any]) -> ProductionEventData | SensorReadingData | DefectData:
    if topic == STATION_EVENTS_TOPIC:
        return map_station_event(raw_event)

    if topic == SENSOR_READINGS_TOPIC:
        return map_sensor_reading_event(raw_event)

    if topic == QUALITY_DEFECTS_TOPIC:
        return map_defect_event(raw_event)

    raise InvalidEventError(f"Unsupported topic: {topic}")
