from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Equipment, Plant, ProductionLine, Station, Vehicle
from app.schemas import (
    EquipmentResponse,
    PlantResponse,
    ProductionLineResponse,
    StationResponse,
    VehicleResponse,
)

router = APIRouter(prefix="/api/v1", tags=["manufacturing domain"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("/plants", response_model=list[PlantResponse])
def list_plants(session: SessionDependency) -> list[Plant]:
    return list(session.scalars(select(Plant).order_by(Plant.code)).all())


@router.get("/lines", response_model=list[ProductionLineResponse])
def list_lines(session: SessionDependency) -> list[ProductionLine]:
    return list(session.scalars(select(ProductionLine).order_by(ProductionLine.code)).all())


@router.get("/stations", response_model=list[StationResponse])
def list_stations(session: SessionDependency) -> list[Station]:
    return list(session.scalars(select(Station).order_by(Station.line_id, Station.sequence_order)).all())


@router.get("/equipment", response_model=list[EquipmentResponse])
def list_equipment(session: SessionDependency) -> list[Equipment]:
    return list(session.scalars(select(Equipment).order_by(Equipment.asset_tag)).all())


@router.get("/vehicles", response_model=list[VehicleResponse])
def list_vehicles(session: SessionDependency) -> list[Vehicle]:
    return list(session.scalars(select(Vehicle).order_by(Vehicle.vin)).all())


@router.get("/vehicles/{vin}", response_model=VehicleResponse)
def get_vehicle(vin: str, session: SessionDependency) -> Vehicle:
    vehicle = session.scalar(select(Vehicle).where(Vehicle.vin == vin))

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle
