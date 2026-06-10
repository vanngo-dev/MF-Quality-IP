from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Equipment, QualityAlert, Station
from app.schemas import AlertResponse, CreateAlertRequest, UpdateAlertStatusRequest

router = APIRouter(prefix="/api/v1/alerts", tags=["quality alerts"])

SessionDependency = Annotated[Session, Depends(get_session)]


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


@router.get("", response_model=list[AlertResponse])
def list_alerts(session: SessionDependency) -> list[QualityAlert]:
    return list(session.scalars(select(QualityAlert).order_by(QualityAlert.created_at.desc(), QualityAlert.id.desc())).all())


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(request: CreateAlertRequest, session: SessionDependency) -> QualityAlert:
    _require_station(session, request.station_id)
    _require_equipment(session, request.equipment_id)

    alert = QualityAlert(**request.model_dump())
    session.add(alert)
    session.commit()
    session.refresh(alert)

    return alert


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, session: SessionDependency) -> QualityAlert:
    alert = session.get(QualityAlert, alert_id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: int,
    request: UpdateAlertStatusRequest,
    session: SessionDependency,
) -> QualityAlert:
    alert = session.get(QualityAlert, alert_id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = request.status
    session.add(alert)
    session.commit()
    session.refresh(alert)

    return alert
