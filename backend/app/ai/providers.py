from dataclasses import dataclass, field
from typing import Protocol

from app.ai.schemas import AISummaryContent
from app.config import get_settings


@dataclass(frozen=True)
class AlertEvidence:
    alert_code: str | None
    title: str | None
    description: str | None
    severity: str | None
    evidence_json: dict[str, object] = field(default_factory=dict)
    station_code: str | None = None
    equipment_code: str | None = None


@dataclass(frozen=True)
class DefectEvidence:
    defect_code: str
    description: str
    severity: str
    status: str


@dataclass(frozen=True)
class SensorEvidence:
    metric_name: str
    value: float
    unit: str


@dataclass(frozen=True)
class EventEvidence:
    event_type: str
    payload: dict[str, object]


@dataclass(frozen=True)
class InvestigationEvidenceContext:
    title: str
    summary: str | None
    root_cause_hypothesis: str | None
    evidence_json: dict[str, object]
    alert: AlertEvidence | None = None
    defects: list[DefectEvidence] = field(default_factory=list)
    sensor_readings: list[SensorEvidence] = field(default_factory=list)
    station_events: list[EventEvidence] = field(default_factory=list)


class InvestigationSummaryProvider(Protocol):
    def generate(self, context: InvestigationEvidenceContext) -> AISummaryContent:
        """Generate a structured investigation summary from available platform evidence."""


class MockInvestigationSummaryProvider:
    def generate(self, context: InvestigationEvidenceContext) -> AISummaryContent:
        evidence: list[str] = []
        limitations: list[str] = ["The summary is based only on events and notes stored in the platform."]
        recommended_checks = [
            "Review the linked alert evidence and confirm it matches current station conditions.",
            "Compare recent quality records against adjacent stations or similar equipment.",
        ]

        alert_code = context.alert.alert_code if context.alert else None
        station = context.alert.station_code if context.alert else None
        equipment = context.alert.equipment_code if context.alert else None
        likely_issue = "Insufficient evidence to identify a specific root cause; available records may indicate a quality issue that needs engineering review."
        issue_signals = 0

        if context.alert is not None:
            evidence.append(_alert_evidence_sentence(context.alert))
            if context.alert.evidence_json:
                evidence.append(f"Alert evidence includes {', '.join(sorted(context.alert.evidence_json.keys()))}.")
            else:
                limitations.append("No structured alert evidence_json is available.")
        else:
            limitations.append("No linked alert is available for this investigation.")

        if alert_code and "REPEATED_DEFECT_STATION" in alert_code:
            likely_issue = "Repeated defects may indicate a station-specific process drift based on available alert evidence."
            recommended_checks.append("Verify recent station setup, containment records, and quality checks for repeated defects.")
            issue_signals += 1

        torque_defects = [defect for defect in context.defects if "TORQUE" in defect.defect_code.upper()]
        if torque_defects:
            evidence.append(f"Related defects include {', '.join(sorted({defect.defect_code for defect in torque_defects}))}.")
            likely_issue = "Repeated torque-related defects may indicate a possible torque tool calibration or process drift."
            recommended_checks.append("Verify torque tool calibration history and compare torque results across adjacent stations.")
            issue_signals += 1
        elif not context.defects:
            limitations.append("No related defect records were available for this investigation.")

        low_vision = [
            reading
            for reading in context.sensor_readings
            if "vision_confidence" in reading.metric_name.lower() and reading.value < 0.9
        ]
        if low_vision:
            evidence.append("Sensor evidence includes low vision confidence readings.")
            likely_issue = "Available evidence may indicate a possible vision inspection confidence issue."
            recommended_checks.append("Inspect camera lens condition, lighting, and recent vision model confidence trends.")
            issue_signals += 1

        high_temperature = [
            reading
            for reading in context.sensor_readings
            if "temperature" in reading.metric_name.lower() and reading.value >= 80
        ]
        if high_temperature:
            evidence.append("Sensor evidence includes high equipment temperature readings.")
            likely_issue = "Available evidence may indicate possible equipment thermal drift."
            recommended_checks.append("Check equipment cooling, thermal alarms, and recent maintenance records.")
            issue_signals += 1

        torque_sensor = [
            reading
            for reading in context.sensor_readings
            if "torque" in reading.metric_name.lower() and (reading.value < 40 or reading.value > 45)
        ]
        if torque_sensor:
            values = ", ".join(f"{reading.metric_name}={reading.value:g}{reading.unit}" for reading in torque_sensor[:3])
            evidence.append(f"Sensor reading {values} was outside the expected torque range.")
            likely_issue = "Available torque sensor evidence may indicate a possible torque process or calibration issue."
            recommended_checks.append("Compare torque readings to calibration limits and recent maintenance records.")
            issue_signals += 1

        if not context.sensor_readings:
            limitations.append("No related sensor readings were available.")

        if context.station_events:
            event_types = ", ".join(sorted({event.event_type for event in context.station_events}))
            evidence.append(f"Related station events include {event_types}.")
        else:
            limitations.append("No related station event history was available.")

        if context.summary:
            evidence.append("Investigation notes were available for review.")
        else:
            limitations.append("Investigation summary notes are not yet documented.")

        if context.root_cause_hypothesis:
            evidence.append("Investigation root-cause hypothesis is documented, but it is treated as engineer input rather than confirmed fact.")
        else:
            limitations.append("Root-cause hypothesis is not yet documented.")

        confidence = _confidence_for(issue_signals, evidence)

        if confidence == "low" and "Insufficient evidence" not in likely_issue:
            likely_issue = f"Available evidence may indicate {likely_issue[0].lower()}{likely_issue[1:]}"

        return AISummaryContent(
            likely_issue=likely_issue,
            affected_station=station,
            affected_equipment=equipment,
            evidence=evidence,
            recommended_next_checks=_dedupe(recommended_checks),
            confidence=confidence,
            limitations=_dedupe(limitations),
        )


class OpenAICompatibleSummaryProvider:
    def generate(self, context: InvestigationEvidenceContext) -> AISummaryContent:
        raise RuntimeError("OpenAI-compatible summary provider is a future placeholder and is not enabled by default.")


def get_investigation_summary_provider() -> InvestigationSummaryProvider:
    provider = get_settings().ai_summary_provider.lower()

    if provider == "mock":
        return MockInvestigationSummaryProvider()

    if provider == "openai_compatible":
        return OpenAICompatibleSummaryProvider()

    return MockInvestigationSummaryProvider()


def _alert_evidence_sentence(alert: AlertEvidence) -> str:
    code = alert.alert_code or "UNKNOWN_ALERT"
    title = alert.title or "untitled alert"
    return f"Alert {code} reported {title}."


def _confidence_for(issue_signals: int, evidence: list[str]) -> str:
    if issue_signals >= 2 and len(evidence) >= 3:
        return "medium"

    return "low"


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []

    for value in values:
        if value not in deduped:
            deduped.append(value)

    return deduped
