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

## Quality Workflows

Phase 3 adds workflow endpoints for defects, alerts, and investigations.

```text
GET /api/v1/defects
POST /api/v1/defects
GET /api/v1/defects/{id}

GET /api/v1/alerts
POST /api/v1/alerts
GET /api/v1/alerts/{id}
PATCH /api/v1/alerts/{id}/status

GET /api/v1/investigations
POST /api/v1/investigations
GET /api/v1/investigations/{id}
PATCH /api/v1/investigations/{id}
```

Defect severities: `low`, `medium`, `high`, `critical`.

Alert severities: `medium`, `high`, `critical`.

Defect statuses: `open`, `investigating`, `contained`, `resolved`.

Alert statuses: `open`, `acknowledged`, `investigating`, `resolved`.

Investigation statuses: `draft`, `active`, `waiting_on_data`, `resolved`.

## Phase 9 Frontend API Usage

The React frontend uses `VITE_API_BASE_URL` to call the FastAPI backend from the browser:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Frontend service functions map to these contracts:

| Frontend function | Backend endpoint |
| --- | --- |
| `getHealth` | `GET /health` |
| `getStations` | `GET /api/v1/stations` |
| `getEquipment` | `GET /api/v1/equipment` |
| `getVehicles` | `GET /api/v1/vehicles` |
| `getVehicleByVin` | `GET /api/v1/vehicles/{vin}` |
| `getDefects` | `GET /api/v1/defects` |
| `getDefectById` | `GET /api/v1/defects/{id}` |
| `getAlerts` | `GET /api/v1/alerts` |
| `getAlertById` | `GET /api/v1/alerts/{id}` |
| `updateAlertStatus` | `PATCH /api/v1/alerts/{id}/status` |
| `getInvestigations` | `GET /api/v1/investigations` |
| `createInvestigation` | `POST /api/v1/investigations` |
| `updateInvestigation` | `PATCH /api/v1/investigations/{id}` |

The investigations API returns `opened_at` and `updated_at`. Phase 9 displays `opened_at` as the created/opened timestamp because the backend does not expose a separate `created_at` field for investigations.

The frontend does not call Elasticsearch or search endpoints in Phase 9. Search starts in Phase 10.

## Phase 10 Search

Search endpoints read from Elasticsearch indexes built from PostgreSQL records.

```text
GET /api/v1/search?q=torque
GET /api/v1/search/defects?q=torque
GET /api/v1/search/alerts?q=defect
GET /api/v1/search/investigations?q=root
GET /api/v1/search/events?q=station
```

Empty or whitespace-only `q` values return `400`:

```json
{
  "detail": "Search query must not be empty."
}
```

Grouped search response:

```json
{
  "query": "torque",
  "results": {
    "defects": [],
    "alerts": [],
    "investigations": [],
    "events": []
  }
}
```

Specialized search response:

```json
{
  "query": "torque",
  "results": []
}
```

Each result includes:

```json
{
  "id": "1",
  "type": "defect",
  "title": "TORQUE_LOW",
  "summary": "Torque value below threshold",
  "score": 3.5,
  "source": {
    "id": 1,
    "defect_code": "TORQUE_LOW",
    "vin": "MQPLANT0000000001",
    "station_code": "ST-TORQUE"
  }
}
```

Search indexes:

| Index | Source records |
| --- | --- |
| `manufacturing-defects` | `defects` |
| `manufacturing-alerts` | `quality_alerts` |
| `manufacturing-investigations` | `investigations` |
| `manufacturing-events` | `production_events` |

## Example Manual Checks

```powershell
curl http://localhost:8000/api/v1/plants
curl http://localhost:8000/api/v1/lines
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/equipment
curl http://localhost:8000/api/v1/vehicles
curl http://localhost:8000/api/v1/vehicles/MQPLANT0000000001
curl http://localhost:8000/api/v1/defects
curl http://localhost:8000/api/v1/alerts
curl http://localhost:8000/api/v1/investigations
```

## Example Workflow Creates

Replace IDs with values returned from `/api/v1/vehicles`, `/api/v1/stations`, `/api/v1/equipment`, and `/api/v1/alerts`.

```powershell
curl -X POST http://localhost:8000/api/v1/defects `
  -H "Content-Type: application/json" `
  -d "{ \"defect_code\": \"TORQUE_LOW\", \"vehicle_id\": \"REPLACE_WITH_VEHICLE_ID\", \"station_id\": \"REPLACE_WITH_STATION_ID\", \"equipment_id\": null, \"severity\": \"high\", \"description\": \"Torque value below acceptable threshold\", \"status\": \"open\" }"
```

```powershell
curl -X POST http://localhost:8000/api/v1/alerts `
  -H "Content-Type: application/json" `
  -d "{ \"alert_code\": \"REPEATED_DEFECT_STATION\", \"station_id\": \"REPLACE_WITH_STATION_ID\", \"equipment_id\": null, \"severity\": \"high\", \"title\": \"Repeated defects detected\", \"description\": \"Multiple torque defects detected at the same station\", \"evidence_json\": { \"defect_count\": 5, \"window_minutes\": 30 }, \"status\": \"open\" }"
```

```powershell
curl -X POST http://localhost:8000/api/v1/investigations `
  -H "Content-Type: application/json" `
  -d "{ \"alert_id\": \"REPLACE_WITH_ALERT_ID\", \"title\": \"Investigate repeated torque defects\", \"summary\": \"Initial investigation created from quality alert\", \"root_cause_hypothesis\": \"Torque tool may be drifting out of calibration\", \"evidence_json\": { \"source\": \"manual_test\" }, \"status\": \"draft\" }"
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

Defect:

```json
{
  "id": 1,
  "defect_code": "TORQUE_LOW",
  "vehicle_id": 1,
  "station_id": 1,
  "equipment_id": null,
  "severity": "high",
  "description": "Torque value below acceptable threshold",
  "status": "open",
  "detected_at": "2026-06-09T00:00:00Z"
}
```

Alert:

```json
{
  "id": 1,
  "alert_code": "REPEATED_DEFECT_STATION",
  "station_id": 1,
  "equipment_id": null,
  "severity": "high",
  "title": "Repeated defects detected",
  "description": "Multiple torque defects detected at the same station",
  "evidence_json": {
    "defect_count": 5,
    "window_minutes": 30
  },
  "status": "open",
  "created_at": "2026-06-09T00:00:00Z"
}
```

Investigation:

```json
{
  "id": 1,
  "alert_id": 1,
  "title": "Investigate repeated torque defects",
  "summary": "Initial investigation created from quality alert",
  "root_cause_hypothesis": "Torque tool may be drifting out of calibration",
  "evidence_json": {
    "source": "manual_test"
  },
  "status": "draft",
  "opened_at": "2026-06-09T00:00:00Z",
  "updated_at": "2026-06-09T00:00:00Z",
  "closed_at": null
}
```
