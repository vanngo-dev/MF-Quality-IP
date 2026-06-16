from __future__ import annotations

from sqlalchemy import func, select

from app.services.alert_service import AlertService, InMemoryAlertPublisher
from app.services.persistence import quality_alerts
from app.tests.test_rule_engine import _alert_candidate, _session_factory


def test_alert_persistence_works() -> None:
    factory = _session_factory()
    publisher = InMemoryAlertPublisher()
    service = AlertService(factory, publisher)

    result = service.create_alert(_alert_candidate())

    with factory() as session:
        saved = session.execute(select(quality_alerts.c.alert_code, quality_alerts.c.status)).one()

    assert result.inserted is True
    assert saved.alert_code == "TEST_ALERT"
    assert saved.status == "open"


def test_quality_alerts_publish_function_is_called_when_alert_is_created() -> None:
    factory = _session_factory()
    publisher = InMemoryAlertPublisher()
    service = AlertService(factory, publisher)

    service.create_alert(_alert_candidate())

    assert len(publisher.published) == 1
    assert publisher.published[0]["alert_code"] == "TEST_ALERT"


def test_alert_service_persists_only_one_alert_for_same_candidate() -> None:
    factory = _session_factory()
    service = AlertService(factory)

    service.create_alert(_alert_candidate())
    service.create_alert(_alert_candidate())

    with factory() as session:
        assert session.scalar(select(func.count()).select_from(quality_alerts)) == 1
