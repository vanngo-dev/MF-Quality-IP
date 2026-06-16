from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.orm import Session, sessionmaker

from app.services.alert_service import AlertCreateResult, AlertService
from app.services.event_mapper import DefectData, ProductionEventData, SensorReadingData
from app.services.persistence import PersistenceResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlertCandidate:
    alert_code: str
    station_id: int
    equipment_id: int | None
    severity: str
    title: str
    description: str
    evidence_json: dict[str, object]


@dataclass(frozen=True)
class RuleContext:
    persistence_result: PersistenceResult
    event_data: ProductionEventData | SensorReadingData | DefectData


class QualityRule(Protocol):
    name: str

    def evaluate(self, session: Session, context: RuleContext | None = None) -> list[AlertCandidate]:
        pass


class RuleEngine:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        alert_service: AlertService,
        rules: tuple[QualityRule, ...] | None = None,
    ) -> None:
        if rules is None:
            from app.rules.consecutive_inspection_failures import ConsecutiveInspectionFailuresRule
            from app.rules.defect_spike import DefectSpikeRule
            from app.rules.equipment_temperature import EquipmentTemperatureRule
            from app.rules.repeated_defect_station import RepeatedDefectStationRule
            from app.rules.torque_out_of_tolerance import TorqueOutOfToleranceRule
            from app.rules.vision_confidence import VisionConfidenceRule

            rules = (
                RepeatedDefectStationRule(),
                EquipmentTemperatureRule(),
                TorqueOutOfToleranceRule(),
                VisionConfidenceRule(),
                DefectSpikeRule(),
                ConsecutiveInspectionFailuresRule(),
            )

        self._session_factory = session_factory
        self._alert_service = alert_service
        self._rules = rules

    def evaluate(self, context: RuleContext | None = None) -> list[AlertCandidate]:
        candidates: list[AlertCandidate] = []

        with self._session_factory() as session:
            for rule in self._rules:
                try:
                    candidates.extend(rule.evaluate(session, context))
                except Exception as exc:
                    logger.warning("Rule %s failed without stopping the worker: %s", rule.name, exc)

        return candidates

    def run(self, context: RuleContext | None = None) -> list[AlertCreateResult]:
        try:
            return self._alert_service.create_alerts(self.evaluate(context))
        except Exception as exc:
            logger.warning("Alert creation failed without stopping the worker: %s", exc)
            return []
