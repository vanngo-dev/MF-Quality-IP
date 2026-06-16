from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.services.event_mapper import ProductionEventData
from app.services.persistence import PersistenceService, equipment, metadata, production_events, stations, vehicles


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


def test_duplicate_event_id_is_ignored() -> None:
    factory = _session_factory()
    service = PersistenceService(factory)
    data = ProductionEventData(
        event_id="00000000-0000-0000-0000-000000000201",
        vehicle_external_id="00000000-0000-0000-0000-000000000001",
        station_external_id="00000000-0000-0000-0000-000000000001",
        event_type="station_entered",
        event_timestamp=datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc),
        payload_json={"station_code": "A-BODY", "vin": "MQPLANT0000000001"},
        vin="MQPLANT0000000001",
        station_code="A-BODY",
    )

    first = service.save_production_event(data)
    second = service.save_production_event(data)

    with factory() as session:
        count = session.scalar(select(func.count()).select_from(production_events))

    assert first.inserted is True
    assert second.inserted is False
    assert second.reason == "duplicate_event_id"
    assert count == 1
