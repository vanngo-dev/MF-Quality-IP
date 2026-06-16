from __future__ import annotations

from app.services.event_mapper import QUALITY_DEFECTS_TOPIC, map_defect_event
from app.services.persistence import PersistenceResult, PersistenceService


class DefectEventConsumer:
    topic = QUALITY_DEFECTS_TOPIC

    def __init__(self, persistence: PersistenceService) -> None:
        self._persistence = persistence

    def handle(self, raw_event: str | bytes) -> PersistenceResult:
        return self._persistence.save_defect(map_defect_event(raw_event))
