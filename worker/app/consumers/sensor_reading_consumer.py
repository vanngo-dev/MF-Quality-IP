from __future__ import annotations

from app.services.event_mapper import SENSOR_READINGS_TOPIC, map_sensor_reading_event
from app.services.persistence import PersistenceResult, PersistenceService
from app.rules.engine import RuleContext, RuleEngine


class SensorReadingConsumer:
    topic = SENSOR_READINGS_TOPIC

    def __init__(self, persistence: PersistenceService, rule_engine: RuleEngine | None = None) -> None:
        self._persistence = persistence
        self._rule_engine = rule_engine

    def handle(self, raw_event: str | bytes) -> PersistenceResult:
        data = map_sensor_reading_event(raw_event)
        result = self._persistence.save_sensor_reading(data)

        if result.inserted and self._rule_engine is not None:
            self._rule_engine.run(RuleContext(persistence_result=result, event_data=data))

        return result
