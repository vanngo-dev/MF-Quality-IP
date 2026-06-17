from datetime import datetime
from typing import Any

from app.models import Defect, Equipment, Investigation, ProductionEvent, QualityAlert

DEFECT_INDEX = "manufacturing-defects"
ALERT_INDEX = "manufacturing-alerts"
INVESTIGATION_INDEX = "manufacturing-investigations"
EVENT_INDEX = "manufacturing-events"

INDEX_NAMES = {
    "defects": DEFECT_INDEX,
    "alerts": ALERT_INDEX,
    "investigations": INVESTIGATION_INDEX,
    "events": EVENT_INDEX,
}

DEFAULT_INDEX_MAPPING = {
    "mappings": {
        "dynamic": True,
        "properties": {
            "type": {"type": "keyword"},
            "status": {"type": "keyword"},
            "severity": {"type": "keyword"},
            "vin": {"type": "keyword"},
            "station_code": {"type": "keyword"},
            "equipment_code": {"type": "keyword"},
        },
    },
}


def ensure_indexes(client: Any) -> None:
    for index_name in INDEX_NAMES.values():
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, **DEFAULT_INDEX_MAPPING)


def index_defect(client: Any, defect: Defect) -> dict[str, Any]:
    document = build_defect_document(defect)
    client.index(index=DEFECT_INDEX, id=str(document["id"]), document=document)
    return document


def index_alert(client: Any, alert: QualityAlert) -> dict[str, Any]:
    document = build_alert_document(alert)
    client.index(index=ALERT_INDEX, id=str(document["id"]), document=document)
    return document


def index_investigation(client: Any, investigation: Investigation) -> dict[str, Any]:
    document = build_investigation_document(investigation)
    client.index(index=INVESTIGATION_INDEX, id=str(document["id"]), document=document)
    return document


def index_event_summary(client: Any, event: ProductionEvent) -> dict[str, Any]:
    document = build_event_summary_document(event)
    client.index(index=EVENT_INDEX, id=str(document["id"]), document=document)
    return document


def build_defect_document(defect: Defect) -> dict[str, Any]:
    return {
        "id": defect.id,
        "defect_code": defect.defect_code,
        "vehicle_id": defect.vehicle_id,
        "vin": getattr(defect.vehicle, "vin", None),
        "station_id": defect.station_id,
        "station_code": getattr(defect.station, "code", None),
        "equipment_id": defect.equipment_id,
        "equipment_code": _equipment_code(defect.equipment),
        "severity": defect.severity,
        "status": defect.status,
        "description": defect.description,
        "detected_at": _isoformat(defect.detected_at),
        "created_at": _isoformat(defect.created_at),
        "type": "defect",
    }


def build_alert_document(alert: QualityAlert) -> dict[str, Any]:
    return {
        "id": alert.id,
        "alert_code": alert.alert_code,
        "station_id": alert.station_id,
        "station_code": getattr(alert.station, "code", None),
        "equipment_id": alert.equipment_id,
        "equipment_code": _equipment_code(alert.equipment),
        "severity": alert.severity,
        "status": alert.status,
        "title": alert.title,
        "description": alert.description,
        "evidence_json": alert.evidence_json or {},
        "created_at": _isoformat(alert.created_at),
        "type": "alert",
    }


def build_investigation_document(investigation: Investigation) -> dict[str, Any]:
    return {
        "id": investigation.id,
        "alert_id": investigation.alert_id,
        "title": investigation.title,
        "summary": investigation.summary,
        "root_cause_hypothesis": investigation.root_cause_hypothesis,
        "ai_summary": None,
        "status": investigation.status,
        "created_at": _isoformat(investigation.opened_at),
        "updated_at": _isoformat(investigation.updated_at),
        "type": "investigation",
    }


def build_event_summary_document(event: ProductionEvent) -> dict[str, Any]:
    payload = event.payload or {}

    return {
        "id": event.id,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "vehicle_id": event.vehicle_id,
        "vin": getattr(event.vehicle, "vin", None),
        "station_id": event.station_id,
        "station_code": getattr(event.station, "code", None),
        "equipment_id": payload.get("equipment_id"),
        "equipment_code": payload.get("equipment_code") or payload.get("equipment_asset_tag"),
        "payload_json": payload,
        "event_timestamp": _isoformat(event.occurred_at),
        "created_at": _isoformat(event.created_at),
        "type": "event",
    }


def _equipment_code(equipment: Equipment | None) -> str | None:
    return getattr(equipment, "asset_tag", None) if equipment is not None else None


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None

