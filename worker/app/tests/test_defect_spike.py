from __future__ import annotations

from app.rules.defect_spike import DefectSpikeRule
from app.tests.test_rule_engine import _insert_defect, _session_factory


def test_defect_spike_rule_creates_expected_alert() -> None:
    factory = _session_factory()

    with factory() as session:
        for index in range(5):
            _insert_defect(session, event_id=f"defect-code-{index}", defect_code="torque_out_of_spec", minutes=index)
        session.commit()

        alerts = DefectSpikeRule().evaluate(session)

    assert len(alerts) == 1
    assert alerts[0].alert_code == "DEFECT_CODE_SPIKE"
    assert alerts[0].evidence_json["defect_code"] == "torque_out_of_spec"


def test_defect_spike_rule_does_not_trigger_below_threshold() -> None:
    factory = _session_factory()

    with factory() as session:
        for index in range(4):
            _insert_defect(session, event_id=f"defect-code-{index}", defect_code="torque_out_of_spec", minutes=index)
        session.commit()

        assert DefectSpikeRule().evaluate(session) == []
