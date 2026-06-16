from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.rules.engine import AlertCandidate, RuleContext, RuleEngine
from app.rules.equipment_temperature import EquipmentTemperatureRule
from app.services.alert_service import AlertService, InMemoryAlertPublisher
from app.services.event_mapper import SensorReadingData
from app.services.persistence import (
    PersistenceService,
    defects,
    equipment,
    metadata,
    production_events,
    quality_alerts,
    sensor_readings,
    stations,
    utc_now,
    vehicles,
)


def _timestamp(minutes: int = 0) -> datetime:
    return datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


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


def _insert_defect(
    session: Session,
    *,
    event_id: str,
    defect_code: str = "torque_out_of_spec",
    station_id: int = 1,
    equipment_id: int | None = 1,
    minutes: int = 0,
) -> None:
    session.execute(
        defects.insert().values(
            event_id=event_id,
            defect_code=defect_code,
            vehicle_id=1,
            station_id=station_id,
            equipment_id=equipment_id,
            severity="high",
            status="open",
            description="Rule test defect",
            detected_at=_timestamp(minutes),
            created_at=utc_now(),
        )
    )


def _insert_sensor(
    session: Session,
    *,
    event_id: str,
    metric_name: str,
    value: float,
    minutes: int = 0,
    station_id: int | None = 1,
    equipment_id: int = 1,
) -> None:
    session.execute(
        sensor_readings.insert().values(
            event_id=event_id,
            equipment_id=equipment_id,
            station_id=station_id,
            metric_name=metric_name,
            value=value,
            unit="C" if metric_name == "temperature_c" else "Nm",
            recorded_at=_timestamp(minutes),
            created_at=utc_now(),
        )
    )


def _insert_inspection(session: Session, *, event_id: str, result: str, minutes: int) -> None:
    session.execute(
        production_events.insert().values(
            event_id=event_id,
            vehicle_id=1,
            station_id=1,
            event_type="inspection_completed",
            occurred_at=_timestamp(minutes),
            payload={"result": result},
            created_at=utc_now(),
        )
    )


def _alert_candidate() -> AlertCandidate:
    return AlertCandidate(
        alert_code="TEST_ALERT",
        station_id=1,
        equipment_id=1,
        severity="medium",
        title="Test alert",
        description="Test alert description",
        evidence_json={"source": "test"},
    )


def test_rule_engine_can_run_after_event_persistence() -> None:
    factory = _session_factory()
    publisher = InMemoryAlertPublisher()
    engine = RuleEngine(factory, AlertService(factory, publisher), rules=(EquipmentTemperatureRule(),))
    persistence = PersistenceService(factory)
    data = SensorReadingData(
        event_id="00000000-0000-0000-0000-000000100001",
        equipment_external_id="00000000-0000-0000-0000-000000000001",
        station_external_id="00000000-0000-0000-0000-000000000001",
        reading_type="temperature_c",
        reading_value=91.2,
        unit="C",
        reading_timestamp=_timestamp(),
        equipment_code="EQ-A-TORQUE-02",
        station_code="A-BODY",
    )

    result = persistence.save_sensor_reading(data)
    alerts = engine.run(RuleContext(result, data))

    assert result.inserted is True
    assert alerts[0].inserted is True
    assert publisher.published[0]["alert_code"] == "EQUIPMENT_TEMPERATURE_HIGH"


def test_rule_engine_does_not_crash_on_rule_error() -> None:
    class FailingRule:
        name = "failing_rule"

        def evaluate(self, session: Session, context: RuleContext | None = None) -> list[AlertCandidate]:
            raise ValueError("bad data")

    factory = _session_factory()
    engine = RuleEngine(factory, AlertService(factory), rules=(FailingRule(),))

    assert engine.run() == []


def test_rule_engine_handles_incomplete_data_without_crashing() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_sensor(session, event_id="sensor-no-station", metric_name="temperature_c", value=91.2, station_id=None)
        session.commit()

    engine = RuleEngine(factory, AlertService(factory), rules=(EquipmentTemperatureRule(),))

    assert engine.run() == []


def test_alert_count() -> None:
    factory = _session_factory()
    alert_service = AlertService(factory)

    alert_service.create_alert(_alert_candidate())

    with factory() as session:
        assert session.scalar(select(func.count()).select_from(quality_alerts)) == 1
