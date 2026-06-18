# Phase 12 — AI-Assisted Investigation Summary

## Goal

Add AI-assisted investigation summary generation using only real available evidence from alerts, defects, sensor readings, station events, and investigation notes.

The project starts with a deterministic mock provider so local demos and tests work without paid APIs or external API keys.

## What Was Built

Phase 12 adds:

- persisted `investigations.ai_summary` JSON field
- Alembic migration for the summary field
- AI summary schemas
- provider interface
- deterministic mock provider
- OpenAI-compatible provider placeholder
- investigation evidence gathering service
- `POST /api/v1/investigations/{id}/ai-summary`
- frontend Generate AI Summary button
- frontend AI Summary panel
- backend guardrail tests
- frontend AI summary tests

## Why This Matters for Manufacturing Quality

Quality engineers often need to assemble facts from several places before they can decide what to check next. AI can help organize that evidence, but it must not invent a root cause.

Phase 12 treats AI as an assistant, not an authority. The summary uses only platform evidence and always displays limitations.

## AI Summary Architecture

The flow is:

```text
Investigation Detail -> Generate AI Summary -> backend evidence gathering -> provider -> saved ai_summary JSON -> frontend panel
```

Evidence sources:

- alert details
- alert `evidence_json`
- related defects
- related sensor readings
- related station events
- investigation title
- investigation summary
- root-cause hypothesis
- existing investigation `evidence_json`

## Provider Interface

The backend has a provider interface:

```text
InvestigationSummaryProvider
```

Implementations:

- `MockInvestigationSummaryProvider`
- `OpenAICompatibleSummaryProvider`

Default configuration:

```text
AI_SUMMARY_PROVIDER=mock
```

Optional future configuration:

```text
OPENAI_COMPATIBLE_BASE_URL=
OPENAI_COMPATIBLE_API_KEY=
OPENAI_COMPATIBLE_MODEL=
```

The OpenAI-compatible provider is a placeholder. The app does not require these values.

## Mock Provider

The mock provider is deterministic. It inspects available evidence and returns a structured summary.

Example behavior:

- repeated-defect alerts mention repeated defects
- torque defects mention possible torque process or calibration issues
- out-of-range torque readings are included as evidence
- low vision confidence readings mention possible vision inspection issues
- high temperature readings mention possible thermal drift
- thin evidence produces low confidence and clear limitations

## Evidence Grounding

The summary output includes:

- likely issue
- affected station
- affected equipment
- evidence list
- recommended next checks
- confidence
- limitations

Summaries are saved to:

```text
investigations.ai_summary
```

The backend also updates:

```text
investigations.updated_at
```

## Guardrails

The summary must:

- only use available evidence
- avoid invented root causes
- state when evidence is missing
- always include limitations
- avoid certainty
- use language such as `may indicate`, `possible`, and `based on available evidence`
- avoid recommending production shutdown unless existing platform evidence clearly supports it

High confidence should be rare. The mock provider currently returns `low` or `medium`.

## Backend API Endpoint

```text
POST /api/v1/investigations/{id}/ai-summary
```

Example response:

```json
{
  "investigation_id": 1,
  "ai_summary": {
    "likely_issue": "Repeated torque defects may indicate a possible torque tool calibration or process drift.",
    "affected_station": "ST-TORQUE",
    "affected_equipment": "EQ-TQ-01",
    "evidence": [
      "Alert REPEATED_DEFECT_STATION reported Repeated defects detected.",
      "Related defects include TORQUE_LOW."
    ],
    "recommended_next_checks": [
      "Verify torque tool calibration history and compare torque results across adjacent stations."
    ],
    "confidence": "medium",
    "limitations": [
      "The summary is based only on events and notes stored in the platform."
    ]
  }
}
```

Missing investigations return `404`.

## Frontend AI Summary Panel

The Investigation Detail page includes:

- Generate AI Summary button
- loading state while generating
- error state if generation fails
- likely issue
- affected station
- affected equipment
- evidence list
- recommended next checks
- confidence badge
- limitations list

If no summary exists, the page shows Generate AI Summary. If a summary already exists, the page displays it and allows regeneration.

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

Create alert and investigation data through the UI or existing APIs.

Generate summary by API:

```powershell
curl -X POST http://localhost:8000/api/v1/investigations/REPLACE_WITH_INVESTIGATION_ID/ai-summary
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
http://localhost:5173/investigations
```

## Automated Tests

Backend:

```powershell
cd backend
pytest
```

Backend tests cover:

- structured mock summary output
- alert evidence usage
- defect evidence usage
- sensor evidence usage
- limitations for missing evidence
- no invented root-cause claim with minimal evidence
- low confidence with thin evidence
- medium confidence when multiple evidence sources agree
- endpoint success
- missing investigation `404`
- summary persistence
- `updated_at` refresh
- no external network requirement

Frontend:

```powershell
cd frontend
npm run test
```

Frontend tests cover:

- Generate AI Summary button
- mutation call
- loading state
- summary likely issue
- evidence list
- recommended next checks
- confidence
- limitations
- error state
- existing saved summary display

## Manual Tests

1. Start services.
2. Run migrations.
3. Seed the database.
4. Create alert and investigation data.
5. Start the backend API.
6. Start the frontend.
7. Open `http://localhost:5173/investigations`.
8. Open an investigation detail page.
9. Click Generate AI Summary.
10. Confirm loading appears.
11. Confirm summary appears.
12. Verify likely issue, evidence, next checks, confidence, and limitations are visible.
13. Confirm the summary uses alert or investigation evidence.
14. Refresh the page.
15. Confirm the saved summary still appears.

## Expected Results

- AI summary endpoint works.
- Mock provider returns deterministic structured summary.
- Summary is saved to investigation.
- Frontend displays summary clearly.
- No external API key is required.
- Missing evidence produces limitations.
- Root cause is not invented.
- Tests pass in a normal local environment.
- No Phase 13 end-to-end tests are added.

## Common Errors and Fixes

### No investigation exists

Create an investigation from an alert before generating a summary.

### Investigation has no linked alert

Use the alert-to-investigation workflow when possible.

### No evidence_json available

The summary will still generate, but limitations will explain missing evidence.

### Summary appears too generic because evidence is thin

Add or ingest relevant defects, sensor readings, station events, or investigation notes.

### AI summary not saved because ai_summary field is missing

Run migrations:

```powershell
cd backend
alembic upgrade head
```

### Migration needed for ai_summary column

Run:

```powershell
cd backend
alembic upgrade head
```

### Frontend mutation succeeds but page does not refresh

Confirm the investigation detail query is invalidated after summary generation.

### Backend not running

Start the backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### CORS error

Confirm:

```text
FRONTEND_ORIGIN=http://localhost:5173
```

### Developer expected OpenAI API but project defaults to mock provider

This is expected. Use:

```text
AI_SUMMARY_PROVIDER=mock
```

## Git Commit

```bash
git add .
git commit -m "phase-12 ai assisted investigation summaries"
```
