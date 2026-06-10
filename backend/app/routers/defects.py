from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Defect, Equipment, Station, Vehicle
from app.schemas import CreateDefectRequest, DefectResponse

router = APIRouter(prefix="/api/v1/defects", tags=["defects"])

SessionDependency = Annotated[Session, Depends(get_session)]


def _require_vehicle(session: Session, vehicle_id: int) -> Vehicle:
    vehicle = session.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle


def _require_station(session: Session, station_id: int) -> Station:
    station = session.get(Station, station_id)

    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")

    return station


def _require_equipment(session: Session, equipment_id: int | None) -> Equipment | None:
    if equipment_id is None:
        return None

    equipment = session.get(Equipment, equipment_id)

    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return equipment


@router.get("", response_model=list[DefectResponse])
def list_defects(session: SessionDependency) -> list[Defect]:
    return list(session.scalars(select(Defect).order_by(Defect.detected_at.desc(), Defect.id.desc())).all())


@router.post("", response_model=DefectResponse, status_code=status.HTTP_201_CREATED)
def create_defect(request: CreateDefectRequest, session: SessionDependency) -> Defect:
    _require_vehicle(session, request.vehicle_id)
    _require_station(session, request.station_id)
    _require_equipment(session, request.equipment_id)

    defect = Defect(**request.model_dump())
    session.add(defect)
    session.commit()
    session.refresh(defect)

    return defect


@router.get("/{defect_id}", response_model=DefectResponse)
def get_defect(defect_id: int, session: SessionDependency) -> Defect:
    defect = session.get(Defect, defect_id)

    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")

    return defect
