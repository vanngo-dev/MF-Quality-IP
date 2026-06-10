from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from random import Random
from uuid import UUID, uuid4

from app.generators.defects import build_defect_event, random_defect_details
from app.generators.sensor_readings import SENSOR_SPECS, build_sensor_reading_event, random_sensor_value
from app.generators.station_events import build_station_event
from app.schemas.events import BaseEvent, ReadingType, StationEventType


BASE_TIME = datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class ManufacturingContext:
    plant_id: UUID
    line_id: UUID
    station_id: UUID
    equipment_id: UUID
    vehicle_id: UUID
    station_code: str
    equipment_code: str
    vin: str
    operator_shift: str


DETERMINISTIC_CONTEXT = ManufacturingContext(
    plant_id=UUID("00000000-0000-0000-0000-000000000001"),
    line_id=UUID("00000000-0000-0000-0000-000000000101"),
    station_id=UUID("00000000-0000-0000-0000-000000001001"),
    equipment_id=UUID("00000000-0000-0000-0000-000000002001"),
    vehicle_id=UUID("00000000-0000-0000-0000-000000010001"),
    station_code="TORQUE_CHECK_02",
    equipment_code="TORQUE_TOOL_02",
    vin="DEMO-VIN-0001",
    operator_shift="A",
)


def _event_id(sequence: int) -> UUID:
    return UUID(f"00000000-0000-0000-0000-{sequence:012d}")


def generate_deterministic_events() -> list[BaseEvent]:
    context = DETERMINISTIC_CONTEXT

    return [
        build_station_event(
            event_id=_event_id(1),
            event_type="station_entered",
            event_timestamp=BASE_TIME,
            plant_id=context.plant_id,
            line_id=context.line_id,
            station_id=context.station_id,
            equipment_id=None,
            vehicle_id=context.vehicle_id,
            station_code=context.station_code,
            vin=context.vin,
            operator_shift=context.operator_shift,
        ),
        build_station_event(
            event_id=_event_id(2),
            event_type="operation_completed",
            event_timestamp=BASE_TIME + timedelta(seconds=45),
            plant_id=context.plant_id,
            line_id=context.line_id,
            station_id=context.station_id,
            equipment_id=context.equipment_id,
            vehicle_id=context.vehicle_id,
            station_code=context.station_code,
            vin=context.vin,
            operator_shift=context.operator_shift,
            result="pass",
            cycle_time_seconds=45.0,
        ),
        build_sensor_reading_event(
            event_id=_event_id(3),
            event_timestamp=BASE_TIME + timedelta(minutes=1),
            plant_id=context.plant_id,
            line_id=context.line_id,
            station_id=context.station_id,
            equipment_id=context.equipment_id,
            vehicle_id=context.vehicle_id,
            reading_type="torque_nm",
            reading_value=42.7,
            equipment_code=context.equipment_code,
        ),
        build_station_event(
            event_id=_event_id(4),
            event_type="inspection_completed",
            event_timestamp=BASE_TIME + timedelta(seconds=90),
            plant_id=context.plant_id,
            line_id=context.line_id,
            station_id=context.station_id,
            equipment_id=context.equipment_id,
            vehicle_id=context.vehicle_id,
            station_code=context.station_code,
            vin=context.vin,
            operator_shift=context.operator_shift,
            result="pass",
            cycle_time_seconds=18.0,
        ),
        build_defect_event(
            event_id=_event_id(5),
            event_timestamp=BASE_TIME + timedelta(minutes=2),
            plant_id=context.plant_id,
            line_id=context.line_id,
            station_id=context.station_id,
            equipment_id=context.equipment_id,
            vehicle_id=context.vehicle_id,
            defect_code="torque_out_of_spec",
            severity="high",
        ),
        build_station_event(
            event_id=_event_id(6),
            event_type="station_exited",
            event_timestamp=BASE_TIME + timedelta(minutes=3),
            plant_id=context.plant_id,
            line_id=context.line_id,
            station_id=context.station_id,
            equipment_id=None,
            vehicle_id=context.vehicle_id,
            station_code=context.station_code,
            vin=context.vin,
            operator_shift=context.operator_shift,
            result="hold_for_quality_review",
        ),
    ]


def _random_context(random: Random) -> ManufacturingContext:
    station_number = random.randint(1, 6)
    vehicle_number = random.randint(1, 9999)
    line_number = random.choice((101, 102))

    return ManufacturingContext(
        plant_id=UUID("00000000-0000-0000-0000-000000000001"),
        line_id=UUID(f"00000000-0000-0000-0000-{line_number:012d}"),
        station_id=UUID(f"00000000-0000-0000-0000-{1000 + station_number:012d}"),
        equipment_id=UUID(f"00000000-0000-0000-0000-{2000 + station_number:012d}"),
        vehicle_id=uuid4(),
        station_code=random.choice(("BODY_FIT_01", "TORQUE_CHECK_02", "PAINT_SCAN_03", "FINAL_GATE_04")),
        equipment_code=random.choice(("TORQUE_TOOL_02", "VISION_CAMERA_03", "PRESSURE_TEST_04", "END_OF_LINE_TESTER")),
        vin=f"DEMO-VIN-{vehicle_number:04d}",
        operator_shift=random.choice(("A", "B", "C")),
    )


def _random_station_event(random: Random, timestamp: datetime) -> BaseEvent:
    context = _random_context(random)
    event_type: StationEventType = random.choice(
        ("station_entered", "operation_completed", "inspection_completed", "station_exited", "rework_required")
    )

    return build_station_event(
        event_type=event_type,
        event_timestamp=timestamp,
        plant_id=context.plant_id,
        line_id=context.line_id,
        station_id=context.station_id,
        equipment_id=None if event_type in {"station_entered", "station_exited"} else context.equipment_id,
        vehicle_id=context.vehicle_id,
        station_code=context.station_code,
        vin=context.vin,
        operator_shift=context.operator_shift,
        result="needs_rework" if event_type == "rework_required" else random.choice(("pass", "pass", "pass", "review")),
        cycle_time_seconds=round(random.uniform(20.0, 180.0), 2),
    )


def _random_sensor_event(random: Random, timestamp: datetime) -> BaseEvent:
    context = _random_context(random)
    reading_type: ReadingType = random.choice(tuple(SENSOR_SPECS.keys()))

    return build_sensor_reading_event(
        event_timestamp=timestamp,
        plant_id=context.plant_id,
        line_id=context.line_id,
        station_id=context.station_id,
        equipment_id=context.equipment_id,
        vehicle_id=context.vehicle_id,
        reading_type=reading_type,
        reading_value=random_sensor_value(reading_type, random),
        equipment_code=context.equipment_code,
    )


def _random_defect_event(random: Random, timestamp: datetime) -> BaseEvent:
    context = _random_context(random)
    defect_code, severity = random_defect_details(random)

    return build_defect_event(
        event_timestamp=timestamp,
        plant_id=context.plant_id,
        line_id=context.line_id,
        station_id=context.station_id,
        equipment_id=context.equipment_id,
        vehicle_id=context.vehicle_id,
        defect_code=defect_code,
        severity=severity,
    )


def generate_random_events(count: int, seed: int | None = None) -> list[BaseEvent]:
    if count < 1:
        raise ValueError("count must be greater than 0")

    random = Random(seed)
    builders = (_random_station_event, _random_sensor_event, _random_defect_event)
    events: list[BaseEvent] = []

    for index in range(count):
        timestamp = BASE_TIME + timedelta(seconds=index * random.randint(15, 90))
        builder = random.choice(builders)
        events.append(builder(random, timestamp))

    return events
