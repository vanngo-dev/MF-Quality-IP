from __future__ import annotations

from app.services.event_mapper import STATION_EVENTS_TOPIC, map_station_event
from app.services.persistence import PersistenceResult, PersistenceService


class StationEventConsumer:
    topic = STATION_EVENTS_TOPIC

    def __init__(self, persistence: PersistenceService) -> None:
        self._persistence = persistence

    def handle(self, raw_event: str | bytes) -> PersistenceResult:
        return self._persistence.save_production_event(map_station_event(raw_event))
