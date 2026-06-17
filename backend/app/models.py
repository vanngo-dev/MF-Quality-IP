from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    lines: Mapped[list[ProductionLine]] = relationship(back_populates="plant", cascade="all, delete-orphan")


class ProductionLine(Base):
    __tablename__ = "production_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    product_family: Mapped[str] = mapped_column(String(80))

    plant: Mapped[Plant] = relationship(back_populates="lines")
    stations: Mapped[list[Station]] = relationship(back_populates="line", cascade="all, delete-orphan")
    vehicles: Mapped[list[Vehicle]] = relationship(back_populates="line")


class Station(Base):
    __tablename__ = "stations"
    __table_args__ = (UniqueConstraint("line_id", "code", name="uq_station_line_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    line_id: Mapped[int] = mapped_column(ForeignKey("production_lines.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(120))
    sequence_order: Mapped[int]

    line: Mapped[ProductionLine] = relationship(back_populates="stations")
    equipment: Mapped[list[Equipment]] = relationship(back_populates="station", cascade="all, delete-orphan")
    defects: Mapped[list[Defect]] = relationship(back_populates="station")
    alerts: Mapped[list[QualityAlert]] = relationship(back_populates="station")


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    asset_tag: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    equipment_type: Mapped[str] = mapped_column(String(80))

    station: Mapped[Station] = relationship(back_populates="equipment")
    sensor_readings: Mapped[list[SensorReading]] = relationship(back_populates="equipment")
    defects: Mapped[list[Defect]] = relationship(back_populates="equipment")
    alerts: Mapped[list[QualityAlert]] = relationship(back_populates="equipment")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(String(17), unique=True, index=True)
    model: Mapped[str] = mapped_column(String(80))
    model_year: Mapped[int]
    color: Mapped[str] = mapped_column(String(40))
    line_id: Mapped[int] = mapped_column(ForeignKey("production_lines.id"), index=True)
    current_station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id"), nullable=True, index=True)
    build_status: Mapped[str] = mapped_column(String(40), default="in_progress")

    line: Mapped[ProductionLine] = relationship(back_populates="vehicles")
    current_station: Mapped[Station | None] = relationship()
    production_events: Mapped[list[ProductionEvent]] = relationship(back_populates="vehicle")
    defects: Mapped[list[Defect]] = relationship(back_populates="vehicle")


class ProductionEvent(Base):
    __tablename__ = "production_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    payload: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    vehicle: Mapped[Vehicle] = relationship(back_populates="production_events")
    station: Mapped[Station] = relationship()


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True, index=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), index=True)
    station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id"), nullable=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(80), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(40))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    equipment: Mapped[Equipment] = relationship(back_populates="sensor_readings")
    station: Mapped[Station | None] = relationship()


class Defect(Base):
    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True, index=True)
    defect_code: Mapped[str] = mapped_column(String(80), index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)
    description: Mapped[str] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    vehicle: Mapped[Vehicle] = relationship(back_populates="defects")
    station: Mapped[Station] = relationship(back_populates="defects")
    equipment: Mapped[Equipment | None] = relationship(back_populates="defects")


class QualityAlert(Base):
    __tablename__ = "quality_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"), nullable=True, index=True)
    alert_code: Mapped[str] = mapped_column(String(60), index=True)
    severity: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    station: Mapped[Station] = relationship(back_populates="alerts")
    equipment: Mapped[Equipment | None] = relationship(back_populates="alerts")
    investigations: Mapped[list[Investigation]] = relationship(back_populates="alert")


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("quality_alerts.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause_hypothesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    alert: Mapped[QualityAlert] = relationship(back_populates="investigations")

    @property
    def created_at(self) -> datetime:
        return self.opened_at

    @property
    def ai_summary(self) -> None:
        return None
