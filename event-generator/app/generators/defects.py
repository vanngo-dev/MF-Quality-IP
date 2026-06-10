from __future__ import annotations

from datetime import datetime
from random import Random
from uuid import UUID, uuid4

from app.schemas.events import DefectCode, DefectEvent, DefectPayload, DefectSeverity


DEFECT_TEMPLATES: dict[DefectCode, dict[str, float | str]] = {
    "torque_out_of_spec": {
        "description": "Torque value below required threshold",
        "measured_value": 36.8,
        "expected_min": 40.0,
        "expected_max": 45.0,
    },
    "vision_low_confidence": {
        "description": "Vision system confidence below acceptance threshold",
        "measured_value": 0.71,
        "expected_min": 0.85,
        "expected_max": 1.0,
    },
    "temperature_excursion": {
        "description": "Station temperature exceeded expected process window",
        "measured_value": 91.4,
        "expected_min": 18.0,
        "expected_max": 85.0,
    },
    "vibration_anomaly": {
        "description": "Vibration level exceeded equipment baseline",
        "measured_value": 10.6,
        "expected_min": 0.0,
        "expected_max": 7.5,
    },
    "pressure_drop": {
        "description": "Pneumatic pressure dropped below process limit",
        "measured_value": 251.2,
        "expected_min": 280.0,
        "expected_max": 360.0,
    },
    "inspection_failure": {
        "description": "Inspection criteria failed at quality gate",
        "measured_value": 0.0,
        "expected_min": 1.0,
        "expected_max": 1.0,
    },
}


def build_defect_event(
    *,
    event_timestamp: datetime,
    plant_id: UUID,
    line_id: UUID,
    station_id: UUID,
    equipment_id: UUID | None,
    vehicle_id: UUID,
    defect_code: DefectCode,
    severity: DefectSeverity,
    event_id: UUID | None = None,
) -> DefectEvent:
    template = DEFECT_TEMPLATES[defect_code]
    payload = DefectPayload(
        defect_code=defect_code,
        severity=severity,
        description=str(template["description"]),
        measured_value=float(template["measured_value"]),
        expected_min=float(template["expected_min"]),
        expected_max=float(template["expected_max"]),
    )

    return DefectEvent(
        event_id=event_id or uuid4(),
        event_timestamp=event_timestamp,
        plant_id=plant_id,
        line_id=line_id,
        station_id=station_id,
        equipment_id=equipment_id,
        vehicle_id=vehicle_id,
        payload=payload,
    )


def random_defect_details(random: Random) -> tuple[DefectCode, DefectSeverity]:
    defect_codes = tuple(DEFECT_TEMPLATES.keys())
    severities: tuple[DefectSeverity, ...] = ("medium", "high", "critical")

    return random.choice(defect_codes), random.choice(severities)
