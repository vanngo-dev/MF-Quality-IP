# Phase 3: Defect, Alert, and Investigation APIs

## Goal

Add the core quality workflow REST APIs for defects, quality alerts, and investigations.

## What This Phase Establishes

- Defect create, list, and detail endpoints.
- Alert create, list, detail, and status update endpoints.
- Investigation create, list, detail, and update endpoints.
- Typed Pydantic request and response schemas.
- Business validation for severity and status values.
- Foreign-key validation for vehicles, stations, equipment, and alerts.

## Why It Matters

Manufacturing quality work is not just data storage. Teams need a workflow: record a defect, raise an alert when the defect pattern matters, and open an investigation to track root-cause work.

## Run Database and Seed Data

```powershell
docker compose up postgres
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

If editable install is not available:

```powershell
pip install fastapi "uvicorn[standard]" pytest httpx pydantic-settings sqlalchemy alembic psycopg2-binary
```

## Run Tests

```powershell
cd backend
pytest
```

## Run API

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## Manual Checks

```powershell
curl http://localhost:8000/api/v1/vehicles
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/defects
curl http://localhost:8000/api/v1/alerts
curl http://localhost:8000/api/v1/investigations
```

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

## Troubleshooting

- If a create endpoint returns `404`, confirm the referenced vehicle, station, equipment, or alert exists.
- If a create or update endpoint returns `422`, check the allowed severity and status values.
- If workflow lists are empty, create records with the POST examples.
- If migrations fail, confirm PostgreSQL is running and `alembic upgrade head` is executed from `backend`.
