from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.ai.schemas import AISummaryContent


DefectSeverity = Literal["low", "medium", "high", "critical"]
AlertSeverity = Literal["medium", "high", "critical"]
DefectStatus = Literal["open", "investigating", "contained", "resolved"]
AlertStatus = Literal["open", "acknowledged", "investigating", "resolved"]
InvestigationStatus = Literal["draft", "active", "waiting_on_data", "resolved"]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    environment: str
    dependencies: dict[str, str] = Field(default_factory=dict)


class ORMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PlantResponse(ORMResponse):
    id: int
    code: str
    name: str
    location: str


class ProductionLineResponse(ORMResponse):
    id: int
    plant_id: int
    code: str
    name: str
    product_family: str


class StationResponse(ORMResponse):
    id: int
    line_id: int
    code: str
    name: str
    sequence_order: int


class EquipmentResponse(ORMResponse):
    id: int
    station_id: int
    asset_tag: str
    name: str
    equipment_type: str


class VehicleResponse(ORMResponse):
    id: int
    vin: str
    model: str
    model_year: int
    color: str
    line_id: int
    current_station_id: int | None
    build_status: str


class CreateDefectRequest(BaseModel):
    defect_code: str
    vehicle_id: int
    station_id: int
    equipment_id: int | None = None
    severity: DefectSeverity
    description: str
    status: DefectStatus = "open"


class DefectResponse(ORMResponse):
    id: int
    defect_code: str
    vehicle_id: int
    station_id: int
    equipment_id: int | None
    severity: str
    description: str
    status: str
    detected_at: datetime


class CreateAlertRequest(BaseModel):
    alert_code: str
    station_id: int
    equipment_id: int | None = None
    severity: AlertSeverity
    title: str
    description: str
    evidence_json: dict[str, object] = Field(default_factory=dict)
    status: AlertStatus = "open"


class UpdateAlertStatusRequest(BaseModel):
    status: AlertStatus


class AlertResponse(ORMResponse):
    id: int
    alert_code: str
    station_id: int
    equipment_id: int | None
    severity: str
    title: str
    description: str
    evidence_json: dict[str, object]
    status: str
    created_at: datetime


class CreateInvestigationRequest(BaseModel):
    alert_id: int
    title: str
    summary: str | None = None
    root_cause_hypothesis: str | None = None
    evidence_json: dict[str, object] = Field(default_factory=dict)
    status: InvestigationStatus = "draft"


class CreateInvestigationFromAlertRequest(BaseModel):
    title: str
    summary: str | None = None
    root_cause_hypothesis: str | None = None
    status: InvestigationStatus = "active"


class UpdateInvestigationRequest(BaseModel):
    title: str | None = None
    summary: str | None = None
    root_cause_hypothesis: str | None = None
    evidence_json: dict[str, object] | None = None
    status: InvestigationStatus | None = None


class UpdateInvestigationStatusRequest(BaseModel):
    status: InvestigationStatus


class InvestigationResponse(ORMResponse):
    id: int
    alert_id: int
    title: str
    summary: str | None
    root_cause_hypothesis: str | None
    evidence_json: dict[str, object]
    ai_summary: AISummaryContent | None
    status: str
    created_at: datetime
    opened_at: datetime
    updated_at: datetime
    closed_at: datetime | None
