# Phase 11 — Quality Investigation Workflow

## Goal

Create the complete manual engineer investigation workflow.

This phase lets a quality engineer move from an alert to an investigation, review evidence, add a root-cause hypothesis, update notes and status, and resolve the investigation and related alert.

AI-assisted summaries are not included in Phase 11. AI summary generation starts in Phase 12.

## What Was Built

Phase 11 adds:

- `POST /api/v1/alerts/{id}/investigation`
- `PATCH /api/v1/investigations/{id}/status`
- duplicate active investigation prevention
- alert evidence copied into new investigations
- alert status update to `investigating` when an investigation is created from an open or acknowledged alert
- investigation resolution behavior that sets `closed_at`
- related alert resolution when an investigation is resolved
- alert detail route at `/alerts/:id`
- investigation detail route at `/investigations/:id`
- `AlertDetailPage`
- `InvestigationDetailPage`
- `InvestigationForm`
- `EvidencePanel`
- `TimelinePanel`
- `InvestigationStatusActions`
- `AlertStatusActions`
- search result links to alert and investigation details
- backend workflow tests
- frontend workflow tests with mocked API responses

## Why This Matters for Manufacturing Quality

Alerts identify risks or recurring quality patterns. Investigations are where engineers collect evidence, record their working hypothesis, document notes, and drive the issue to resolution.

The workflow keeps the original alert evidence attached to the investigation so engineers can see why the investigation was opened and what facts were known at the start.

## Investigation Workflow

The workflow is:

```text
alert detail -> evidence review -> create investigation -> edit summary and root-cause hypothesis -> update status -> resolve investigation and alert
```

Engineers can:

- open alert detail
- view alert evidence
- create an investigation from the alert
- add or update a root-cause hypothesis
- add or update summary notes
- change investigation status
- resolve the investigation
- resolve or update the related alert

## Backend API Endpoints

Existing endpoints continue to work:

```text
GET /api/v1/alerts
GET /api/v1/alerts/{id}
PATCH /api/v1/alerts/{id}/status
GET /api/v1/investigations
POST /api/v1/investigations
GET /api/v1/investigations/{id}
PATCH /api/v1/investigations/{id}
```

Phase 11 adds:

```text
POST /api/v1/alerts/{id}/investigation
PATCH /api/v1/investigations/{id}/status
```

Create investigation from alert:

```json
{
  "title": "Investigate repeated torque defects",
  "summary": "Initial investigation opened from quality alert.",
  "root_cause_hypothesis": "Torque tool may be drifting out of calibration.",
  "status": "active"
}
```

If an active investigation already exists for the alert, the backend returns `409`.

## Frontend Pages

Routes added:

```text
/alerts/:id
/investigations/:id
```

`AlertDetailPage` shows:

- alert title
- alert code
- severity
- status
- station and equipment context
- description
- evidence JSON
- created timestamp
- alert status actions
- create investigation form
- link to an existing active investigation

`InvestigationDetailPage` shows:

- title
- status
- linked alert
- summary
- root-cause hypothesis
- evidence JSON
- AI summary placeholder
- created timestamp
- updated timestamp
- edit form
- investigation status actions
- related alert status actions

## Evidence Panel

`EvidencePanel` displays structured `evidence_json` as pretty-printed JSON.

Evidence matters because it captures the facts that created the alert, such as defect count, time window, station, equipment, threshold, or rule evidence.

## Status Transitions

Allowed investigation statuses:

- `draft`
- `active`
- `waiting_on_data`
- `resolved`

Allowed alert statuses:

- `open`
- `acknowledged`
- `investigating`
- `resolved`

Creating an investigation from an open or acknowledged alert changes the alert status to `investigating`.

Resolving an investigation sets `closed_at` and updates the related alert to `resolved`.

Updating an investigation refreshes `updated_at`.

## How to Run It

Start services:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Run backend setup:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
pytest
python -m uvicorn app.main:app --reload --port 8000
```

If editable install is not supported:

```powershell
pip install fastapi "uvicorn[standard]" pytest httpx pydantic-settings sqlalchemy alembic psycopg2-binary elasticsearch
```

Create alert data if needed.

Option 1: use Phase 7 defect spike:

```powershell
cd worker
python -m app.main
```

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Option 2: use direct API POST:

```powershell
curl -X POST http://localhost:8000/api/v1/alerts `
  -H "Content-Type: application/json" `
  -d "{ \"alert_code\": \"REPEATED_DEFECT_STATION\", \"station_id\": \"REPLACE_WITH_STATION_ID\", \"equipment_id\": null, \"severity\": \"high\", \"title\": \"Repeated defects detected\", \"description\": \"Multiple torque defects detected at the same station\", \"evidence_json\": { \"defect_count\": 5, \"window_minutes\": 30 }, \"status\": \"open\" }"
```

Start frontend:

```powershell
cd frontend
npm install
npm run test
npm run dev
```

Open:

```text
http://localhost:5173/alerts
```

## Automated Tests

Backend:

```powershell
cd backend
pytest
```

Backend tests cover:

- create investigation from alert success
- missing alert failure
- alert status update to `investigating`
- duplicate active investigation prevention
- summary update
- root-cause hypothesis update
- status update
- invalid status validation
- resolve investigation
- related alert resolution
- investigation evidence detail
- alert detail still works

Frontend:

```powershell
cd frontend
npm run test
```

Frontend tests cover:

- alert detail page rendering
- evidence panel rendering
- create investigation form rendering
- create investigation mutation
- investigation detail page rendering
- summary update form
- root-cause hypothesis update form
- investigation status update
- JSON evidence panel
- timeline panel
- search result link to alert detail

## Manual Tests

1. Start local services.
2. Run migrations.
3. Seed the database.
4. Start the backend API.
5. Create or ingest at least one alert.
6. Start the frontend.
7. Open `http://localhost:5173/alerts`.
8. Click an alert.
9. Review the evidence panel.
10. Click Create Investigation.
11. Enter title, summary, and root-cause hypothesis.
12. Save the investigation.
13. Confirm the alert status changes to `investigating`.
14. Open the investigation detail page.
15. Edit the summary.
16. Edit the root-cause hypothesis.
17. Change status to `waiting_on_data`.
18. Resolve the investigation.
19. Confirm the investigation persists as `resolved`.
20. Confirm the related alert is `resolved`.

Manual API checks:

```powershell
curl http://localhost:8000/api/v1/alerts
curl http://localhost:8000/api/v1/investigations
```

## Expected Results

- Alert detail page loads.
- Evidence panel displays alert evidence.
- Investigation can be created from alert.
- Duplicate active investigation is prevented.
- Investigation detail page loads.
- Investigation can be edited.
- Investigation status can change.
- Resolved investigation persists.
- Related alert status updates to `resolved`.
- Tests pass in a normal local environment.
- No Phase 12 AI summary generation is added.

## Common Errors and Fixes

### No alerts exist to investigate

Create an alert through the API or run the Phase 7 defect spike flow.

### Alert ID not found

Use an ID returned by:

```powershell
curl http://localhost:8000/api/v1/alerts
```

### Duplicate investigation already exists for alert

Open the existing active investigation or resolve it before creating another one.

### Investigation status validation fails

Use one of:

```text
draft
active
waiting_on_data
resolved
```

### Frontend route does not load because route path is missing

Confirm these routes exist:

```text
/alerts/:id
/investigations/:id
```

### Mutation succeeds but UI does not refresh

Confirm the frontend invalidates related alert and investigation queries after mutations.

### CORS error

Confirm:

```text
FRONTEND_ORIGIN=http://localhost:5173
```

### Backend not running

Start the backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Database not migrated

Run:

```powershell
cd backend
alembic upgrade head
```

### Seed data missing

Run:

```powershell
cd backend
python -m app.db.seed
```

## Git Commit

```bash
git add .
git commit -m "phase-11 quality investigation workflow"
```
