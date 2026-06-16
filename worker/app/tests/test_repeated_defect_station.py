from __future__ import annotations

from app.rules.repeated_defect_station import RepeatedDefectStationRule
from app.tests.test_rule_engine import _insert_defect, _session_factory


def test_repeated_defect_station_rule_creates_expected_alert() -> None:
    factory = _session_factory()

    with factory() as session:
        for index in range(5):
            _insert_defect(session, event_id=f"defect-{index}", minutes=index)
        session.commit()

        alerts = RepeatedDefectStationRule().evaluate(session)

    assert len(alerts) == 1
    assert alerts[0].alert_code == "REPEATED_DEFECT_STATION"
    assert alerts[0].severity == "high"
    assert alerts[0].evidence_json["defect_count"] == 5


def test_repeated_defect_station_rule_does_not_trigger_below_threshold() -> None:
    factory = _session_factory()

    with factory() as session:
        for index in range(4):
            _insert_defect(session, event_id=f"defect-{index}", minutes=index)
        session.commit()

        assert RepeatedDefectStationRule().evaluate(session) == []
