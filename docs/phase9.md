# Phase 9 — Dashboard Data Integration

## Goal

Connect the React + TypeScript frontend pages to live FastAPI backend API data using TanStack Query.

This phase turns the Phase 8 dashboard shell into a working internal manufacturing quality dashboard. It does not add Elasticsearch search, AI summaries, or the full investigation detail workflow.

## What Was Built

Phase 9 updates the existing `frontend/` app instead of rewriting it.

It adds:

- live API calls for dashboard, stations, equipment, vehicles, defects, alerts, and investigations
- `VITE_API_BASE_URL` usage for backend origin configuration
- TanStack Query loading, error, success, refetch, and mutation flows
- live dashboard metrics calculated from backend responses
- stations table with defect and alert counts calculated client-side
- equipment table with station labels
- vehicles table with VIN search, selected vehicle details, selected vehicle defects, and current station
- defects table with severity and status filters
- alerts table with severity and status filters
- alert acknowledgement with `PATCH /api/v1/alerts/{id}/status`
- investigations table using backend investigation records
- frontend tests with mocked API responses

## Why This Matters for Manufacturing Quality

Manufacturing quality teams need a dashboard that reflects the current plant state. Static placeholders are useful for layout work, but live data is what lets users see active defects, alerts, vehicle context, station impact, and investigation follow-up.

Phase 9 connects the UI to the backend system of record while keeping the frontend testable without requiring Docker or a running API.

## Frontend-to-Backend Flow

The Phase 9 browser flow is:

```text
React route -> TanStack Query -> frontend API service -> FastAPI backend -> PostgreSQL
```

The frontend reads:

```text
VITE_API_BASE_URL=http://localhost:8000
```

from `.env.example` or local environment files. If the variable is missing, the frontend falls back to `http://localhost:8000`.

TanStack Query is used because backend data is server state. It handles:

- loading states while requests are pending
- error states when the backend is unavailable or returns an error
- success states when data arrives
- refetching dashboard data
- invalidating alert data after acknowledgement

## API Endpoints Used

Phase 9 uses existing backend endpoints:

```text
GET /health
GET /api/v1/stations
GET /api/v1/equipment
GET /api/v1/vehicles
GET /api/v1/vehicles/{vin}
GET /api/v1/defects
GET /api/v1/defects/{id}
GET /api/v1/alerts
GET /api/v1/alerts/{id}
PATCH /api/v1/alerts/{id}/status
GET /api/v1/investigations
GET /api/v1/investigations/{id}
POST /api/v1/investigations
PATCH /api/v1/investigations/{id}
```

The FastAPI backend lives in `backend/`. This repo does not use an `api/` folder.

## Dashboard Metrics

The dashboard calculates:

- total vehicles from `/api/v1/vehicles`
- open defects from `/api/v1/defects`
- open alerts from `/api/v1/alerts`
- critical alerts from `/api/v1/alerts`
- top defect station by counting defects per station
- latest sensor event timestamp

The backend does not expose a sensor event detail API in this phase, so latest sensor event displays:

```text
Not available yet
```

Vehicle station event history is also deferred and displays:

```text
Station event history will be added in a later phase.
```

## Pages Connected

Connected pages:

- Dashboard
- Stations
- Equipment
- Vehicles
- Defects
- Alerts
- Investigations

The root route still redirects to `/dashboard`.

Stations show station code, station name, station type, line ID, defect count, and alert count.

Equipment shows equipment code, type, station, and status.

Vehicles show all vehicles, support VIN search, show selected vehicle details, show selected vehicle defects, and display the current station when available.

Defects show defect code, vehicle, station, equipment, severity, status, detected timestamp, and description.

Alerts show alert code, title, station, equipment, severity, status, created timestamp, description, and actions.

Investigations show title, alert ID, status, root-cause hypothesis, created/opened timestamp, and updated timestamp. The backend returns `opened_at`, so Phase 9 displays it as the created/opened value.

## Filtering and Mutations

Defects support client-side filters for:

- severity
- status

Alerts support client-side filters for:

- severity
- status

Open alerts show an `Acknowledge` button. Clicking it sends:

```text
PATCH /api/v1/alerts/{id}/status
```

with:

```json
{
  "status": "acknowledged"
}
```

After the mutation succeeds, the alerts query is invalidated so the alert table refreshes from the backend.

The `Open Investigation` action routes to `/investigations`. The full investigation detail workflow is not built in Phase 9 because it belongs to Phase 11.

Search is not included in Phase 9 because Elasticsearch search starts in Phase 10.

## How to Run It

Start backend services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed:

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

Start the backend API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Optional: start the worker if you want live defects and alerts created from streamed events:

```powershell
cd worker
python -m app.main
```

Optional: produce demo events and alerts:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Start the frontend:

```powershell
cd frontend
npm install
npm run test
npm run dev
```

Open:

```text
http://localhost:5173
```

## Automated Tests

Frontend tests:

```powershell
cd frontend
npm run test
```

Frontend tests cover:

- API client URL construction
- dashboard loading state
- dashboard error state
- dashboard live stats from mocked API data
- stations table
- equipment table
- vehicles table
- VIN search and selected VIN details
- defects table
- defect severity filter
- defect status filter
- alerts table
- alert severity filter
- alert status filter
- alert acknowledgement mutation
- investigations table

Existing backend tests:

```powershell
cd backend
pytest
```

Existing worker tests:

```powershell
cd worker
pytest
```

Existing event-generator tests:

```powershell
cd event-generator
pytest
```

## Manual Tests

1. Start PostgreSQL, Redpanda, and Redpanda Console.
2. Run backend migrations.
3. Seed the backend database.
4. Start the backend API on port 8000.
5. Start the frontend on port 5173.
6. Open `http://localhost:5173`.
7. Confirm the dashboard displays live data.
8. Confirm stations load real station data.
9. Confirm equipment loads real equipment data.
10. Confirm vehicles load real vehicle data.
11. Search for a VIN and confirm selected vehicle details appear.
12. Confirm defects load real defect data.
13. Filter defects by severity and status.
14. Confirm alerts load real alert data.
15. Filter alerts by severity and status.
16. Acknowledge an open alert and confirm its status updates.
17. Confirm investigations load real investigation data.
18. Stop the backend and confirm error states appear.
19. Confirm there are no browser console errors.

## Expected Results

- Frontend starts on port 5173.
- Backend starts on port 8000.
- Dashboard uses backend API data.
- Navigation works.
- Tables render live data.
- Filters work.
- VIN search works.
- Alert acknowledge action works.
- Tests pass in a normal local environment.
- No Elasticsearch search is added.
- No full Phase 11 investigation workflow is added.

## Common Errors and Fixes

### Frontend cannot connect to backend

Confirm the backend API is running:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Wrong VITE_API_BASE_URL

Set:

```text
VITE_API_BASE_URL=http://localhost:8000
```

### Backend not running

Start the API from `backend/`:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

### CORS error

The backend is configured to allow the local frontend origin. Confirm the frontend is running at:

```text
http://localhost:5173
```

### Database not seeded

Run:

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

### No defects or alerts visible because worker/event generator has not run

Start the worker and publish demo events:

```powershell
cd worker
python -m app.main
```

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

### Alert acknowledge fails because PATCH endpoint is missing or wrong

Confirm the backend exposes:

```text
PATCH /api/v1/alerts/{id}/status
```

### React Query cache not refreshing after mutation

Confirm the alert acknowledgement mutation invalidates the `alerts` query after success.

### Port 5173 already in use

Run the frontend on another port:

```powershell
npm run dev -- --port 5174
```

### Port 8000 already in use

Stop the existing backend process or run the backend on another port and update `VITE_API_BASE_URL`.

## Git Commit

```bash
git add .
git commit -m "phase-9 frontend dashboard data integration"
```
