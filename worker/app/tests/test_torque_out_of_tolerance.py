from __future__ import annotations

from app.rules.torque_out_of_tolerance import TorqueOutOfToleranceRule
from app.tests.test_rule_engine import _insert_sensor, _session_factory


def test_torque_out_of_tolerance_rule_creates_expected_alert() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_sensor(session, event_id="torque-high", metric_name="torque_nm", value=47.2)
        session.commit()

        alerts = TorqueOutOfToleranceRule().evaluate(session)

    assert len(alerts) == 1
    assert alerts[0].alert_code == "TORQUE_OUT_OF_TOLERANCE"
    assert alerts[0].evidence_json["upper_limit"] == 45.0


def test_torque_out_of_tolerance_rule_does_not_trigger_inside_limits() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_sensor(session, event_id="torque-ok", metric_name="torque_nm", value=42.2)
        session.commit()

        assert TorqueOutOfToleranceRule().evaluate(session) == []
