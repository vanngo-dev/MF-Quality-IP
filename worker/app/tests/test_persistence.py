from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.services.event_mapper import DefectData, ProductionEventData, SensorReadingData
from app.services.persistence import (
    PersistenceService,
    defects,
    equipment,
    metadata,
    production_events,
    sensor_readings,
    stations,
    vehicles,
)


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with factory() as session:
        session.execute(vehicles.insert().values(id=1, vin="MQPLANT0000000001"))
        session.execute(stations.insert().values(id=1, code="A-BODY"))
        session.execute(equipment.insert().values(id=1, station_id=1, asset_tag="EQ-A-TORQUE-02"))
        session.commit()

    return factory


def _timestamp() -> datetime:
    return datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc)


def test_persistence_service_can_save_a_production_event() -> None:
    service = PersistenceService(_session_factory())
    data = ProductionEventData(
        event_id="00000000-0000-0000-0000-000000000101",
        vehicle_external_id="00000000-0000-0000-0000-000000000001",
        station_external_id="00000000-0000-0000-0000-000000000001",
        event_type="station_entered",
        event_timestamp=_timestamp(),
        payload_json={"station_code": "A-BODY", "vin": "MQPLANT0000000001"},
        vin="MQPLANT0000000001",
        station_code="A-BODY",
    )

    result = service.save_production_event(data)

    assert result.inserted is True
    assert result.table_name == "production_events"


def test_persistence_service_can_save_a_sensor_reading() -> None:
    factory = _session_factory()
    service = PersistenceService(factory)
    data = SensorReadingData(
        event_id="00000000-0000-0000-0000-000000000102",
        equipment_external_id="00000000-0000-0000-0000-000000000001",
        station_external_id="00000000-0000-0000-0000-000000000001",
        reading_type="torque_nm",
        reading_value=42.7,
        unit="Nm",
        reading_timestamp=_timestamp(),
        equipment_code="EQ-A-TORQUE-02",
        station_code="A-BODY",
    )

    result = service.save_sensor_reading(data)

    with factory() as session:
        count = session.scalar(select(func.count()).select_from(sensor_readings))

    assert result.inserted is True
    assert count == 1


def test_persistence_service_can_save_a_defect() -> None:
    factory = _session_factory()
    service = PersistenceService(factory)
    data = DefectData(
        event_id="00000000-0000-0000-0000-000000000103",
        defect_code="torque_out_of_spec",
        vehicle_external_id="00000000-0000-0000-0000-000000000001",
        station_external_id="00000000-0000-0000-0000-000000000001",
        equipment_external_id="00000000-0000-0000-0000-000000000001",
        severity="high",
        description="Torque value below required threshold",
        detected_at=_timestamp(),
        vin="MQPLANT0000000001",
        station_code="A-BODY",
        equipment_code="EQ-A-TORQUE-02",
    )

    result = service.save_defect(data)

    with factory() as session:
        saved = session.execute(select(defects.c.defect_code, defects.c.status)).one()

    assert result.inserted is True
    assert saved.defect_code == "torque_out_of_spec"
    assert saved.status == "open"


def test_persistence_uses_uuid_suffix_when_natural_key_is_absent() -> None:
    factory = _session_factory()
    service = PersistenceService(factory)
    data = ProductionEventData(
        event_id="00000000-0000-0000-0000-000000000104",
        vehicle_external_id="00000000-0000-0000-0000-000000010001",
        station_external_id="00000000-0000-0000-0000-000000001001",
        event_type="station_entered",
        event_timestamp=_timestamp(),
        payload_json={},
    )

    result = service.save_production_event(data)

    with factory() as session:
        saved = session.execute(select(production_events.c.vehicle_id, production_events.c.station_id)).one()

    assert result.inserted is True
    assert saved.vehicle_id == 1
    assert saved.station_id == 1
