# API Contracts

## Health

```text
GET /health
```

Returns the operational health contract created in Phase 1.

## Manufacturing Domain

All Phase 2 domain endpoints are read-only and return JSON arrays unless noted.

```text
GET /api/v1/plants
GET /api/v1/lines
GET /api/v1/stations
GET /api/v1/equipment
GET /api/v1/vehicles
GET /api/v1/vehicles/{vin}
```

## Example Manual Checks

```powershell
curl http://localhost:8000/api/v1/plants
curl http://localhost:8000/api/v1/lines
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/equipment
curl http://localhost:8000/api/v1/vehicles
curl http://localhost:8000/api/v1/vehicles/MQPLANT0000000001
```

## Response Shapes

Plant:

```json
{
  "id": 1,
  "code": "PLT-DET",
  "name": "Detroit Quality Assembly",
  "location": "Detroit, MI"
}
```

Vehicle:

```json
{
  "id": 1,
  "vin": "MQPLANT0000000001",
  "model": "Aster EV",
  "model_year": 2026,
  "color": "Silver",
  "line_id": 1,
  "current_station_id": 1,
  "build_status": "in_progress"
}
```
