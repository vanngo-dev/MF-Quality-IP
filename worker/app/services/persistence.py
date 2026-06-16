from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.services.event_mapper import DefectData, ProductionEventData, SensorReadingData

metadata = MetaData()

vehicles = Table(
    "vehicles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("vin", String(17), unique=True, index=True),
)

stations = Table(
    "stations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("code", String(40), index=True),
)

equipment = Table(
    "equipment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("station_id", Integer, ForeignKey("stations.id"), index=True),
    Column("asset_tag", String(60), unique=True, index=True),
)

production_events = Table(
    "production_events",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("event_id", String(36), unique=True, index=True),
    Column("vehicle_id", Integer, ForeignKey("vehicles.id"), nullable=False, index=True),
    Column("station_id", Integer, ForeignKey("stations.id"), nullable=False, index=True),
    Column("event_type", String(80), nullable=False, index=True),
    Column("occurred_at", DateTime(timezone=True), nullable=False, index=True),
    Column("payload", JSON, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

sensor_readings = Table(
    "sensor_readings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("event_id", String(36), unique=True, index=True),
    Column("equipment_id", Integer, ForeignKey("equipment.id"), nullable=False, index=True),
    Column("station_id", Integer, ForeignKey("stations.id"), nullable=True, index=True),
    Column("metric_name", String(80), nullable=False, index=True),
    Column("value", Float, nullable=False),
    Column("unit", String(40), nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

defects = Table(
    "defects",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("event_id", String(36), unique=True, index=True),
    Column("defect_code", String(80), nullable=False, index=True),
    Column("vehicle_id", Integer, ForeignKey("vehicles.id"), nullable=False, index=True),
    Column("station_id", Integer, ForeignKey("stations.id"), nullable=False, index=True),
    Column("equipment_id", Integer, ForeignKey("equipment.id"), nullable=True, index=True),
    Column("severity", String(40), nullable=False, index=True),
    Column("status", String(40), nullable=False, index=True),
    Column("description", Text, nullable=False),
    Column("detected_at", DateTime(timezone=True), nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


class PersistenceError(RuntimeError):
    """Raised when a valid event cannot be written to the current database state."""


@dataclass(frozen=True)
class PersistenceResult:
    inserted: bool
    table_name: str
    event_id: str
    record_id: int | None = None
    reason: str | None = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_engine(database_url: str) -> Engine:
    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {"pool_pre_ping": True}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine_kwargs["connect_args"] = connect_args

        if ":memory:" in database_url:
            engine_kwargs["poolclass"] = StaticPool

    return create_engine(database_url, **engine_kwargs)


def make_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(bind=make_engine(database_url), autoflush=False, autocommit=False)


class PersistenceService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_production_event(self, data: ProductionEventData) -> PersistenceResult:
        with self._session_factory() as session:
            if self._event_id_exists(session, data.event_id):
                return self._duplicate_result(production_events.name, data.event_id)

            vehicle_id = self._resolve_vehicle_id(session, data.vehicle_external_id, data.vin)
            station_id = self._resolve_station_id(session, data.station_external_id, data.station_code)

            return self._insert(
                session,
                production_events,
                data.event_id,
                {
                    "event_id": data.event_id,
                    "vehicle_id": vehicle_id,
                    "station_id": station_id,
                    "event_type": data.event_type,
                    "occurred_at": data.event_timestamp,
                    "payload": data.payload_json,
                    "created_at": utc_now(),
                },
            )

    def save_sensor_reading(self, data: SensorReadingData) -> PersistenceResult:
        with self._session_factory() as session:
            if self._event_id_exists(session, data.event_id):
                return self._duplicate_result(sensor_readings.name, data.event_id)

            station_id = self._resolve_station_id(session, data.station_external_id, data.station_code)
            equipment_id = self._resolve_equipment_id(session, data.equipment_external_id, data.equipment_code)

            return self._insert(
                session,
                sensor_readings,
                data.event_id,
                {
                    "event_id": data.event_id,
                    "equipment_id": equipment_id,
                    "station_id": station_id,
                    "metric_name": data.reading_type,
                    "value": data.reading_value,
                    "unit": data.unit,
                    "recorded_at": data.reading_timestamp,
                    "created_at": utc_now(),
                },
            )

    def save_defect(self, data: DefectData) -> PersistenceResult:
        with self._session_factory() as session:
            if self._event_id_exists(session, data.event_id):
                return self._duplicate_result(defects.name, data.event_id)

            vehicle_id = self._resolve_vehicle_id(session, data.vehicle_external_id, data.vin)
            station_id = self._resolve_station_id(session, data.station_external_id, data.station_code)
            equipment_id = self._resolve_optional_equipment_id(
                session,
                data.equipment_external_id,
                data.equipment_code,
            )

            return self._insert(
                session,
                defects,
                data.event_id,
                {
                    "event_id": data.event_id,
                    "defect_code": data.defect_code,
                    "vehicle_id": vehicle_id,
                    "station_id": station_id,
                    "equipment_id": equipment_id,
                    "severity": data.severity,
                    "status": data.status,
                    "description": data.description,
                    "detected_at": data.detected_at,
                    "created_at": utc_now(),
                },
            )

    def _insert(
        self,
        session: Session,
        table: Table,
        event_id: str,
        values: dict[str, object],
    ) -> PersistenceResult:
        try:
            result = session.execute(table.insert().values(**values))
            session.commit()
        except IntegrityError as exc:
            session.rollback()

            if self._event_id_exists(session, event_id):
                return self._duplicate_result(table.name, event_id)

            raise PersistenceError(f"Could not persist event {event_id} into {table.name}: {exc}") from exc

        record_id = result.inserted_primary_key[0] if result.inserted_primary_key else None

        return PersistenceResult(inserted=True, table_name=table.name, event_id=event_id, record_id=record_id)

    def _event_id_exists(self, session: Session, event_id: str) -> bool:
        for table in (production_events, sensor_readings, defects):
            existing_id = session.scalar(select(table.c.id).where(table.c.event_id == event_id))

            if existing_id is not None:
                return True

        return False

    @staticmethod
    def _duplicate_result(table_name: str, event_id: str) -> PersistenceResult:
        return PersistenceResult(inserted=False, table_name=table_name, event_id=event_id, reason="duplicate_event_id")

    def _resolve_vehicle_id(self, session: Session, external_id: str, vin: str | None) -> int:
        return self._resolve_required_id(
            session=session,
            table=vehicles,
            external_id=external_id,
            natural_column="vin",
            natural_value=vin,
            offsets=(10000,),
            entity_name="vehicle",
        )

    def _resolve_station_id(self, session: Session, external_id: str, station_code: str | None) -> int:
        return self._resolve_required_id(
            session=session,
            table=stations,
            external_id=external_id,
            natural_column="code",
            natural_value=station_code,
            offsets=(1000,),
            entity_name="station",
        )

    def _resolve_equipment_id(self, session: Session, external_id: str, equipment_code: str | None) -> int:
        return self._resolve_required_id(
            session=session,
            table=equipment,
            external_id=external_id,
            natural_column="asset_tag",
            natural_value=equipment_code,
            offsets=(2000,),
            entity_name="equipment",
        )

    def _resolve_optional_equipment_id(
        self,
        session: Session,
        external_id: str | None,
        equipment_code: str | None,
    ) -> int | None:
        if external_id is None and equipment_code is None:
            return None

        return self._resolve_required_id(
            session=session,
            table=equipment,
            external_id=external_id,
            natural_column="asset_tag",
            natural_value=equipment_code,
            offsets=(2000,),
            entity_name="equipment",
        )

    def _resolve_required_id(
        self,
        *,
        session: Session,
        table: Table,
        external_id: str | None,
        natural_column: str,
        natural_value: str | None,
        offsets: tuple[int, ...],
        entity_name: str,
    ) -> int:
        if natural_value:
            natural_id = session.scalar(select(table.c.id).where(table.c[natural_column] == natural_value))

            if natural_id is not None:
                return int(natural_id)

        for candidate in _external_id_candidates(external_id, offsets):
            candidate_id = session.scalar(select(table.c.id).where(table.c.id == candidate))

            if candidate_id is not None:
                return int(candidate_id)

        raise PersistenceError(
            f"Could not resolve {entity_name} for external_id={external_id!r} natural_value={natural_value!r}."
        )


def _external_id_candidates(external_id: str | None, offsets: tuple[int, ...]) -> list[int]:
    if external_id is None:
        return []

    raw_candidates: list[int] = []

    try:
        parsed = UUID(str(external_id))
    except ValueError:
        if str(external_id).isdigit():
            raw_candidates.append(int(str(external_id)))
    else:
        if 0 < parsed.int <= 2_147_483_647:
            raw_candidates.append(parsed.int)

        tail = str(parsed).rsplit("-", maxsplit=1)[-1]

        if tail.isdigit():
            decimal_tail = int(tail)
            raw_candidates.append(decimal_tail)

            for offset in offsets:
                if decimal_tail > offset:
                    raw_candidates.append(decimal_tail - offset)

    candidates: list[int] = []

    for candidate in raw_candidates:
        if candidate > 0 and candidate not in candidates:
            candidates.append(candidate)

    return candidates
