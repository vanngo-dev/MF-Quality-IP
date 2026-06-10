from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
