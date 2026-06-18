from typing import Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["low", "medium", "high"]


class AISummaryContent(BaseModel):
    likely_issue: str
    affected_station: str | None = None
    affected_equipment: str | None = None
    evidence: list[str] = Field(default_factory=list)
    recommended_next_checks: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel
    limitations: list[str] = Field(default_factory=list)


class AISummaryResponse(BaseModel):
    investigation_id: int
    ai_summary: AISummaryContent
