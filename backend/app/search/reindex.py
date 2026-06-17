from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import SessionLocal
from app.models import Defect, Investigation, ProductionEvent, QualityAlert
from app.search.client import get_elasticsearch_client
from app.search.indexer import ensure_indexes, index_alert, index_defect, index_event_summary, index_investigation


def reindex_search(session: Session | None = None, client: object | None = None) -> dict[str, int]:
    owns_session = session is None
    active_session = session or SessionLocal()
    active_client = client or get_elasticsearch_client()

    try:
        ensure_indexes(active_client)
        counts = {
            "defects": _index_defects(active_session, active_client),
            "alerts": _index_alerts(active_session, active_client),
            "investigations": _index_investigations(active_session, active_client),
            "events": _index_events(active_session, active_client),
        }
    finally:
        if owns_session:
            active_session.close()

    return counts


def main() -> None:
    counts = reindex_search()

    print("Search reindex complete")
    for document_type, count in counts.items():
        print(f"{document_type}: {count}")


def _index_defects(session: Session, client: object) -> int:
    defects = session.scalars(
        select(Defect).options(
            joinedload(Defect.vehicle),
            joinedload(Defect.station),
            joinedload(Defect.equipment),
        ),
    ).all()

    for defect in defects:
        index_defect(client, defect)

    return len(defects)


def _index_alerts(session: Session, client: object) -> int:
    alerts = session.scalars(
        select(QualityAlert).options(
            joinedload(QualityAlert.station),
            joinedload(QualityAlert.equipment),
        ),
    ).all()

    for alert in alerts:
        index_alert(client, alert)

    return len(alerts)


def _index_investigations(session: Session, client: object) -> int:
    investigations = session.scalars(select(Investigation)).all()

    for investigation in investigations:
        index_investigation(client, investigation)

    return len(investigations)


def _index_events(session: Session, client: object) -> int:
    events = session.scalars(
        select(ProductionEvent).options(
            joinedload(ProductionEvent.vehicle),
            joinedload(ProductionEvent.station),
        ),
    ).all()

    for event in events:
        index_event_summary(client, event)

    return len(events)


if __name__ == "__main__":
    main()

