from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.ai.providers import (
    AlertEvidence,
    DefectEvidence,
    EventEvidence,
    InvestigationEvidenceContext,
    InvestigationSummaryProvider,
    SensorEvidence,
    get_investigation_summary_provider,
)
from app.ai.schemas import AISummaryContent
from app.models import Defect, Investigation, ProductionEvent, QualityAlert, SensorReading, utc_now


def generate_and_save_investigation_summary(
    session: Session,
    investigation: Investigation,
    provider: InvestigationSummaryProvider | None = None,
) -> AISummaryContent:
    active_provider = provider or get_investigation_summary_provider()
    context = build_investigation_evidence_context(session, investigation)
    summary = active_provider.generate(context)

    investigation.ai_summary = summary.model_dump()
    investigation.updated_at = _next_updated_at(investigation.updated_at)
    session.add(investigation)
    session.commit()
    session.refresh(investigation)

    return summary


def _next_updated_at(previous: datetime | None) -> datetime:
    current = utc_now()

    if previous is None:
        return current

    if current.replace(tzinfo=None) <= previous.replace(tzinfo=None):
        return previous + timedelta(microseconds=1)

    return current


def build_investigation_evidence_context(
    session: Session,
    investigation: Investigation,
) -> InvestigationEvidenceContext:
    alert = session.get(QualityAlert, investigation.alert_id)
    defects = _related_defects(session, alert)
    sensor_readings = _related_sensor_readings(session, alert)
    station_events = _related_station_events(session, alert)

    return InvestigationEvidenceContext(
        title=investigation.title,
        summary=investigation.summary,
        root_cause_hypothesis=investigation.root_cause_hypothesis,
        evidence_json=investigation.evidence_json or {},
        alert=_alert_evidence(alert),
        defects=[
            DefectEvidence(
                defect_code=defect.defect_code,
                description=defect.description,
                severity=defect.severity,
                status=defect.status,
            )
            for defect in defects
        ],
        sensor_readings=[
            SensorEvidence(metric_name=reading.metric_name, value=reading.value, unit=reading.unit)
            for reading in sensor_readings
        ],
        station_events=[
            EventEvidence(event_type=event.event_type, payload=event.payload or {})
            for event in station_events
        ],
    )


def _alert_evidence(alert: QualityAlert | None) -> AlertEvidence | None:
    if alert is None:
        return None

    return AlertEvidence(
        alert_code=alert.alert_code,
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        evidence_json=alert.evidence_json or {},
        station_code=getattr(alert.station, "code", None),
        equipment_code=getattr(alert.equipment, "asset_tag", None),
    )


def _related_defects(session: Session, alert: QualityAlert | None) -> list[Defect]:
    if alert is None:
        return []

    conditions = [Defect.station_id == alert.station_id]

    if alert.equipment_id is not None:
        conditions.append(Defect.equipment_id == alert.equipment_id)

    return list(
        session.scalars(
            select(Defect)
            .where(or_(*conditions))
            .order_by(Defect.detected_at.desc(), Defect.id.desc())
            .limit(20),
        ).all(),
    )


def _related_sensor_readings(session: Session, alert: QualityAlert | None) -> list[SensorReading]:
    if alert is None:
        return []

    conditions = [SensorReading.station_id == alert.station_id]

    if alert.equipment_id is not None:
        conditions.append(SensorReading.equipment_id == alert.equipment_id)

    return list(
        session.scalars(
            select(SensorReading)
            .where(or_(*conditions))
            .order_by(SensorReading.recorded_at.desc(), SensorReading.id.desc())
            .limit(20),
        ).all(),
    )


def _related_station_events(session: Session, alert: QualityAlert | None) -> list[ProductionEvent]:
    if alert is None:
        return []

    return list(
        session.scalars(
            select(ProductionEvent)
            .where(ProductionEvent.station_id == alert.station_id)
            .order_by(ProductionEvent.occurred_at.desc(), ProductionEvent.id.desc())
            .limit(20),
        ).all(),
    )
