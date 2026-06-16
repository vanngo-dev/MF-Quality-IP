from __future__ import annotations

from app.rules.consecutive_inspection_failures import ConsecutiveInspectionFailuresRule
from app.tests.test_rule_engine import _insert_inspection, _session_factory


def test_consecutive_inspection_failures_rule_creates_expected_alert() -> None:
    factory = _session_factory()

    with factory() as session:
        for index in range(3):
            _insert_inspection(session, event_id=f"inspection-fail-{index}", result="fail", minutes=index)
        session.commit()

        alerts = ConsecutiveInspectionFailuresRule().evaluate(session)

    assert len(alerts) == 1
    assert alerts[0].alert_code == "CONSECUTIVE_INSPECTION_FAILURES"
    assert alerts[0].evidence_json["failure_count"] == 3


def test_consecutive_inspection_failures_rule_does_not_trigger_if_latest_sequence_has_pass() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_inspection(session, event_id="inspection-fail-1", result="fail", minutes=1)
        _insert_inspection(session, event_id="inspection-pass", result="pass", minutes=2)
        _insert_inspection(session, event_id="inspection-fail-2", result="fail", minutes=3)
        session.commit()

        assert ConsecutiveInspectionFailuresRule().evaluate(session) == []
