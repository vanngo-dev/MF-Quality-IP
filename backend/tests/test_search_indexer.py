from datetime import datetime, timezone

from app.models import Defect, Equipment, Investigation, ProductionEvent, QualityAlert, Station, Vehicle
from app.search.indexer import (
    ALERT_INDEX,
    DEFECT_INDEX,
    EVENT_INDEX,
    INVESTIGATION_INDEX,
    build_alert_document,
    build_defect_document,
    build_event_summary_document,
    build_investigation_document,
    ensure_indexes,
    index_defect,
)
from app.search.reindex import reindex_search


def test_indexer_builds_valid_defect_document():
    defect = _defect()

    document = build_defect_document(defect)

    assert document["type"] == "defect"
    assert document["defect_code"] == "TORQUE_LOW"
    assert document["vin"] == "MQPLANT0000000001"
    assert document["station_code"] == "ST-TORQUE"
    assert document["equipment_code"] == "EQ-TQ-01"
    assert document["description"] == "Torque value below threshold"


def test_indexer_builds_valid_alert_document():
    alert = _alert()

    document = build_alert_document(alert)

    assert document["type"] == "alert"
    assert document["alert_code"] == "REPEATED_DEFECT_STATION"
    assert document["station_code"] == "ST-TORQUE"
    assert document["equipment_code"] == "EQ-TQ-01"
    assert document["evidence_json"] == {"defect_count": 3}


def test_indexer_builds_valid_investigation_document():
    investigation = Investigation(
        id=3,
        alert_id=2,
        title="Investigate torque defects",
        summary="Review torque records",
        root_cause_hypothesis="Tool calibration drift",
        evidence_json={},
        status="draft",
        opened_at=_now(),
        updated_at=_now(),
        closed_at=None,
    )

    document = build_investigation_document(investigation)

    assert document["type"] == "investigation"
    assert document["created_at"] == investigation.opened_at.isoformat()
    assert document["updated_at"] == investigation.updated_at.isoformat()
    assert document["ai_summary"] is None


def test_indexer_builds_valid_event_summary_document():
    event = ProductionEvent(
        id=4,
        event_id="event-1",
        vehicle_id=1,
        station_id=1,
        event_type="station_exit",
        payload={"equipment_id": 7, "equipment_code": "EQ-TQ-01"},
        occurred_at=_now(),
        created_at=_now(),
    )
    event.vehicle = _vehicle()
    event.station = _station()

    document = build_event_summary_document(event)

    assert document["type"] == "event"
    assert document["event_id"] == "event-1"
    assert document["vin"] == "MQPLANT0000000001"
    assert document["station_code"] == "ST-TORQUE"
    assert document["equipment_code"] == "EQ-TQ-01"


def test_index_defect_writes_to_defect_index():
    client = FakeElasticsearchClient()

    document = index_defect(client, _defect())

    assert document["id"] == 1
    assert client.indexed[0]["index"] == DEFECT_INDEX
    assert client.indexed[0]["document"]["type"] == "defect"


def test_ensure_indexes_creates_search_indexes():
    client = FakeElasticsearchClient()

    ensure_indexes(client)

    assert client.created_indexes == {DEFECT_INDEX, ALERT_INDEX, INVESTIGATION_INDEX, EVENT_INDEX}


def test_reindex_command_handles_empty_database(session_factory):
    client = FakeElasticsearchClient()

    with session_factory() as session:
        counts = reindex_search(session=session, client=client)

    assert counts == {"defects": 0, "alerts": 0, "investigations": 0, "events": 0}
    assert client.indexed == []


class FakeElasticsearchClient:
    def __init__(self) -> None:
        self.created_indexes: set[str] = set()
        self.indexed: list[dict[str, object]] = []
        self.indices = FakeIndices(self)

    def index(self, index: str, id: str, document: dict[str, object]) -> None:
        self.indexed.append({"index": index, "id": id, "document": document})


class FakeIndices:
    def __init__(self, client: FakeElasticsearchClient) -> None:
        self.client = client

    def exists(self, index: str) -> bool:
        return index in self.client.created_indexes

    def create(self, index: str, **kwargs: object) -> None:
        self.client.created_indexes.add(index)


def _defect() -> Defect:
    defect = Defect(
        id=1,
        event_id="defect-event-1",
        defect_code="TORQUE_LOW",
        vehicle_id=1,
        station_id=1,
        equipment_id=7,
        severity="high",
        status="open",
        description="Torque value below threshold",
        detected_at=_now(),
        created_at=_now(),
    )
    defect.vehicle = _vehicle()
    defect.station = _station()
    defect.equipment = _equipment()
    return defect


def _alert() -> QualityAlert:
    alert = QualityAlert(
        id=2,
        station_id=1,
        equipment_id=7,
        alert_code="REPEATED_DEFECT_STATION",
        severity="critical",
        title="Repeated torque defects",
        description="Multiple torque defects detected",
        evidence_json={"defect_count": 3},
        status="open",
        created_at=_now(),
    )
    alert.station = _station()
    alert.equipment = _equipment()
    return alert


def _vehicle() -> Vehicle:
    return Vehicle(
        id=1,
        vin="MQPLANT0000000001",
        model="Aster EV",
        model_year=2026,
        color="Silver",
        line_id=1,
        current_station_id=1,
        build_status="in_progress",
    )


def _station() -> Station:
    return Station(id=1, line_id=1, code="ST-TORQUE", name="Torque Station", sequence_order=1)


def _equipment() -> Equipment:
    return Equipment(id=7, station_id=1, asset_tag="EQ-TQ-01", name="Torque Tool", equipment_type="Torque Tool")


def _now() -> datetime:
    return datetime(2026, 6, 9, 12, 0, tzinfo=timezone.utc)

