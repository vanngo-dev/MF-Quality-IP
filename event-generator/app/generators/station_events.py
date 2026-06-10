from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from app.schemas.events import StationEvent, StationEventType, StationPayload


def build_station_event(
    *,
    event_type: StationEventType,
    event_timestamp: datetime,
    plant_id: UUID,
    line_id: UUID,
    station_id: UUID,
    vehicle_id: UUID,
    station_code: str,
    vin: str,
    operator_shift: str,
    event_id: UUID | None = None,
    equipment_id: UUID | None = None,
    result: str | None = None,
    cycle_time_seconds: float | None = None,
) -> StationEvent:
    payload = StationPayload(
        station_code=station_code,
        vin=vin,
        operator_shift=operator_shift,
        result=result,
        cycle_time_seconds=cycle_time_seconds,
    )

    return StationEvent(
        event_id=event_id or uuid4(),
        event_type=event_type,
        event_timestamp=event_timestamp,
        plant_id=plant_id,
        line_id=line_id,
        station_id=station_id,
        equipment_id=equipment_id,
        vehicle_id=vehicle_id,
        payload=payload,
    )
