from __future__ import annotations

from app.rules.equipment_temperature import EquipmentTemperatureRule
from app.tests.test_rule_engine import _insert_sensor, _session_factory


def test_equipment_temperature_rule_creates_expected_alert() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_sensor(session, event_id="temp-high", metric_name="temperature_c", value=91.4)
        session.commit()

        alerts = EquipmentTemperatureRule().evaluate(session)

    assert len(alerts) == 1
    assert alerts[0].alert_code == "EQUIPMENT_TEMPERATURE_HIGH"
    assert alerts[0].evidence_json["reading_value"] == 91.4


def test_equipment_temperature_rule_does_not_trigger_below_threshold() -> None:
    factory = _session_factory()

    with factory() as session:
        _insert_sensor(session, event_id="temp-normal", metric_name="temperature_c", value=79.9)
        session.commit()

        assert EquipmentTemperatureRule().evaluate(session) == []
