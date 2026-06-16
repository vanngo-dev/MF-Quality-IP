from __future__ import annotations

from app.rules.vision_confidence import VisionConfidenceRule
from app.tests.test_rule_engine import _insert_sensor, _session_factory


def test_vision_confidence_rule_creates_expected_alert() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_sensor(session, event_id="vision-low", metric_name="vision_confidence", value=0.72)
        session.commit()

        alerts = VisionConfidenceRule().evaluate(session)

    assert len(alerts) == 1
    assert alerts[0].alert_code == "VISION_CONFIDENCE_LOW"
    assert alerts[0].evidence_json["threshold"] == 0.85


def test_vision_confidence_rule_does_not_trigger_above_threshold() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_sensor(session, event_id="vision-ok", metric_name="vision_confidence", value=0.91)
        session.commit()

        assert VisionConfidenceRule().evaluate(session) == []
