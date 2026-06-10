from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.events import BaseEvent, DefectEvent, SensorReadingEvent, StationEvent


VALID_BASE = {
    "event_id": "00000000-0000-0000-0000-000000000001",
    "event_type": "station_entered",
    "event_timestamp": "2026-01-01T08:00:00Z",
    "source": "event-generator",
    "plant_id": "00000000-0000-0000-0000-000000000101",
    "line_id": "00000000-0000-0000-0000-000000000201",
    "station_id": "00000000-0000-0000-0000-000000000301",
    "equipment_id": None,
    "vehicle_id": "00000000-0000-0000-0000-000000000401",
    "payload": {"station_code": "TORQUE_CHECK_02"},
}


def test_base_event_schema_validates_valid_event() -> None:
    event = BaseEvent.model_validate(VALID_BASE)

    assert event.event_id == UUID("00000000-0000-0000-0000-000000000001")
    assert event.event_timestamp == datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)


def test_base_event_schema_rejects_missing_event_id() -> None:
    invalid = VALID_BASE.copy()
    invalid.pop("event_id")

    with pytest.raises(ValidationError):
        BaseEvent.model_validate(invalid)


def test_base_event_schema_rejects_invalid_timestamp() -> None:
    invalid = VALID_BASE | {"event_timestamp": "not-a-date"}

    with pytest.raises(ValidationError):
        BaseEvent.model_validate(invalid)


def test_station_event_validates_station_event_payload() -> None:
    event = StationEvent.model_validate(
        VALID_BASE
        | {
            "payload": {
                "station_code": "TORQUE_CHECK_02",
                "vin": "DEMO-VIN-0001",
                "operator_shift": "A",
                "cycle_time_seconds": 42.5,
            }
        }
    )

    assert event.payload.station_code == "TORQUE_CHECK_02"


def test_sensor_reading_event_validates_reading_type_and_value() -> None:
    event = SensorReadingEvent.model_validate(
        VALID_BASE
        | {
            "event_type": "sensor_reading",
            "equipment_id": "00000000-0000-0000-0000-000000000501",
            "payload": {
                "reading_type": "torque_nm",
                "reading_value": 42.7,
                "unit": "Nm",
                "equipment_code": "TORQUE_TOOL_02",
                "lower_limit": 40.0,
                "upper_limit": 45.0,
            },
        }
    )

    assert event.payload.reading_type == "torque_nm"
    assert event.payload.reading_value == 42.7


def test_defect_event_validates_severity_and_defect_code() -> None:
    event = DefectEvent.model_validate(
        VALID_BASE
        | {
            "event_type": "defect_detected",
            "equipment_id": "00000000-0000-0000-0000-000000000501",
            "payload": {
                "defect_code": "torque_out_of_spec",
                "severity": "high",
                "description": "Torque value below required threshold",
                "measured_value": 36.8,
                "expected_min": 40.0,
                "expected_max": 45.0,
            },
        }
    )

    assert event.payload.defect_code == "torque_out_of_spec"
    assert event.payload.severity == "high"
