from __future__ import annotations

from app.services.event_mapper import SENSOR_READINGS_TOPIC, map_sensor_reading_event
from app.services.persistence import PersistenceResult, PersistenceService


class SensorReadingConsumer:
    topic = SENSOR_READINGS_TOPIC

    def __init__(self, persistence: PersistenceService) -> None:
        self._persistence = persistence

    def handle(self, raw_event: str | bytes) -> PersistenceResult:
        return self._persistence.save_sensor_reading(map_sensor_reading_event(raw_event))
