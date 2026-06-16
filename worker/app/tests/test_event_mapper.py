from __future__ import annotations

from app.services.event_mapper import (
    DefectData,
    ProductionEventData,
    SensorReadingData,
    map_defect_event,
    map_sensor_reading_event,
    map_station_event,
)


def _base_event() -> dict[str, object]:
    return {
        "event_id": "00000000-0000-0000-0000-000000000001",
        "event_type": "station_entered",
        "event_timestamp": "2026-01-01T08:00:00Z",
        "source": "event-generator",
        "plant_id": "00000000-0000-0000-0000-000000000001",
        "line_id": "00000000-0000-0000-0000-000000000101",
        "station_id": "00000000-0000-0000-0000-000000000001",
        "equipment_id": None,
        "vehicle_id": "00000000-0000-0000-0000-000000000001",
        "payload": {},
    }


def test_station_event_maps_to_production_event_data() -> None:
    event = _base_event() | {
        "payload": {
            "station_code": "A-BODY",
            "vin": "MQPLANT0000000001",
            "operator_shift": "A",
            "cycle_time_seconds": 45.0,
        }
    }

    data = map_station_event(event)

    assert isinstance(data, ProductionEventData)
    assert data.event_id == "00000000-0000-0000-0000-000000000001"
    assert data.event_type == "station_entered"
    assert data.station_code == "A-BODY"
    assert data.vin == "MQPLANT0000000001"
    assert data.payload_json["operator_shift"] == "A"


def test_sensor_reading_event_maps_to_sensor_reading_data() -> None:
    event = _base_event() | {
        "event_id": "00000000-0000-0000-0000-000000000002",
        "event_type": "sensor_reading",
        "equipment_id": "00000000-0000-0000-0000-000000000001",
        "payload": {
            "reading_type": "torque_nm",
            "reading_value": 42.7,
            "unit": "Nm",
            "equipment_code": "EQ-A-TORQUE-02",
        },
    }

    data = map_sensor_reading_event(event)

    assert isinstance(data, SensorReadingData)
    assert data.event_id == "00000000-0000-0000-0000-000000000002"
    assert data.reading_type == "torque_nm"
    assert data.reading_value == 42.7
    assert data.unit == "Nm"
    assert data.equipment_code == "EQ-A-TORQUE-02"


def test_defect_event_maps_to_defect_data() -> None:
    event = _base_event() | {
        "event_id": "00000000-0000-0000-0000-000000000003",
        "event_type": "defect_detected",
        "equipment_id": "00000000-0000-0000-0000-000000000001",
        "payload": {
            "defect_code": "torque_out_of_spec",
            "severity": "high",
            "description": "Torque value below required threshold",
        },
    }

    data = map_defect_event(event)

    assert isinstance(data, DefectData)
    assert data.event_id == "00000000-0000-0000-0000-000000000003"
    assert data.defect_code == "torque_out_of_spec"
    assert data.severity == "high"
    assert data.description == "Torque value below required threshold"
    assert data.status == "open"
