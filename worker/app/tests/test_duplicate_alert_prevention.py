from __future__ import annotations

from app.services.alert_service import AlertService
from app.tests.test_rule_engine import _alert_candidate, _session_factory


def test_duplicate_alert_prevention_works() -> None:
    service = AlertService(_session_factory())

    first = service.create_alert(_alert_candidate())
    second = service.create_alert(_alert_candidate())

    assert first.inserted is True
    assert second.inserted is False
    assert second.reason == "duplicate_open_alert"
