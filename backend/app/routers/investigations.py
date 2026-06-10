from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Investigation, QualityAlert
from app.schemas import CreateInvestigationRequest, InvestigationResponse, UpdateInvestigationRequest

router = APIRouter(prefix="/api/v1/investigations", tags=["investigations"])

SessionDependency = Annotated[Session, Depends(get_session)]


def _require_alert(session: Session, alert_id: int) -> QualityAlert:
    alert = session.get(QualityAlert, alert_id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.get("", response_model=list[InvestigationResponse])
def list_investigations(session: SessionDependency) -> list[Investigation]:
    return list(session.scalars(select(Investigation).order_by(Investigation.opened_at.desc(), Investigation.id.desc())).all())


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
def create_investigation(request: CreateInvestigationRequest, session: SessionDependency) -> Investigation:
    _require_alert(session, request.alert_id)

    investigation = Investigation(**request.model_dump())
    session.add(investigation)
    session.commit()
    session.refresh(investigation)

    return investigation


@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(investigation_id: int, session: SessionDependency) -> Investigation:
    investigation = session.get(Investigation, investigation_id)

    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    return investigation


@router.patch("/{investigation_id}", response_model=InvestigationResponse)
def update_investigation(
    investigation_id: int,
    request: UpdateInvestigationRequest,
    session: SessionDependency,
) -> Investigation:
    investigation = session.get(Investigation, investigation_id)

    if investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "evidence_json" and value is None:
            value = {}

        setattr(investigation, field, value)

    session.add(investigation)
    session.commit()
    session.refresh(investigation)

    return investigation
