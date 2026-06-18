# Phase 13 — End-to-End Testing

## Goal

Add Playwright end-to-end tests for the complete manufacturing quality workflow:

```text
Dashboard -> Alerts -> Alert detail -> Create investigation -> Investigation detail -> Generate AI Summary -> Resolve investigation
```

The FastAPI backend remains in `backend/`. This phase does not create an `api/` folder and does not add Phase 14 one-command demo orchestration or Phase 15 CI work.

## What Was Built

- `e2e/` Playwright project.
- `e2e/playwright.config.ts`.
- `e2e/playwright/manufacturing-quality-flow.spec.ts`.
- `e2e/playwright/helpers/api.ts`.
- `e2e/playwright/helpers/test-data.ts`.
- `@playwright/test` dependency in `e2e/package.json`.
- `make test-e2e` shortcut.
- Stable frontend `data-testid` selectors for the critical quality workflow.
- Documentation in README, testing strategy, tutorial notes, and this phase guide.

## Why This Matters for Manufacturing Quality

Manufacturing quality software is useful only if the full workflow holds together. A quality engineer needs to move from an alert to evidence, create an investigation, generate a grounded AI summary, and resolve the issue without losing context.

Unit tests prove small pieces. Integration tests prove APIs and UI data calls. End-to-end tests prove the running frontend and backend work together through the same browser path the user takes.

## E2E Test Strategy

Phase 13 uses API-created fixtures for automated Playwright tests. Before the browser opens the Alerts page, the test calls the backend API to:

- confirm `/health` is reachable;
- read seeded stations and equipment;
- create a fresh quality alert with manufacturing evidence.

This is more stable than depending on Redpanda and worker timing in automated E2E runs. The manual demo still covers the full event-generator to Redpanda to worker to database to UI flow.

## Automated E2E Flow

The Playwright test verifies:

1. Backend health is reachable.
2. Frontend dashboard loads.
3. Seeded or generated alert data is visible.
4. Alerts page loads.
5. User opens an alert detail page.
6. User creates an investigation from the alert.
7. Investigation detail page loads.
8. User generates an AI summary.
9. AI summary appears with likely issue, evidence, recommended checks, confidence, and limitations.
10. User resolves the investigation.
11. Resolved status is visible.

## Manual Full-System Demo Flow

The manual demo uses the whole platform:

```text
event-generator -> Redpanda -> worker -> PostgreSQL -> FastAPI -> React UI
```

Start services:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Run backend setup and API:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start worker:

```powershell
cd worker
pip install -e .
python -m app.main
```

Publish quality demo events:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173/alerts
```

Then open an alert, create an investigation, generate an AI summary, and resolve the investigation.

## Playwright Configuration

Defaults:

```text
baseURL = http://localhost:5173
E2E_FRONTEND_URL=http://localhost:5173
E2E_API_URL=http://localhost:8000
```

The Playwright config stores:

- screenshots on failure;
- video on failure;
- traces on first retry;
- test artifacts in `e2e/test-results/`;
- HTML report in `e2e/playwright-report/`.

## Stable Selectors

Phase 13 adds selectors for:

- `dashboard-page`
- `alerts-page`
- `alert-row`
- `alert-detail-page`
- `create-investigation-button`
- `investigation-form`
- `save-investigation-button`
- `investigation-detail-page`
- `generate-ai-summary-button`
- `ai-summary-panel`
- `investigation-status-select`
- `resolve-investigation-button`

These selectors are intentionally attached only to workflow-critical elements so the UI can keep evolving without breaking tests for visual copy or layout changes.

## How to Run It

Start backend:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

Start frontend:

```powershell
cd frontend
npm install
npm run dev
```

Run Playwright:

```powershell
cd e2e
npm install
npx playwright install
npx playwright test
```

Makefile shortcut:

```powershell
make test-e2e
```

## Automated Tests

Automated E2E coverage includes:

- Playwright config loads.
- E2E can reach frontend.
- E2E can reach backend health.
- E2E alert detail page loads.
- E2E investigation creation works.
- E2E AI summary generation works.
- E2E investigation resolution works.

The automated test uses the mock-first AI summary provider through the existing backend endpoint. It does not require a paid AI API key.

## Manual Tests

Manual verification should confirm:

- Dashboard loads from the running backend.
- Alerts page shows live alert rows.
- Alert detail shows alert evidence.
- Create Investigation opens the form.
- Save Investigation navigates to investigation detail.
- Generate AI Summary fills the summary panel.
- Resolve Investigation updates the status to resolved.
- Related alert is resolved after investigation resolution.

## Expected Results

Successful Playwright output should show the manufacturing quality workflow test passing in Chromium. If a test fails, inspect:

- terminal failure message;
- `e2e/test-results/` screenshot, video, or trace artifacts;
- `e2e/playwright-report/` HTML report.

## Common Errors and Fixes

- Backend not running: start `python -m uvicorn app.main:app --reload --port 8000` from `backend/`.
- Frontend not running: start `npm run dev` from `frontend/`.
- Playwright browsers missing: run `npx playwright install` from `e2e/`.
- Database missing seed data: run `alembic upgrade head` and `python -m app.db.seed` from `backend/`.
- Frontend cannot reach API: confirm `VITE_API_BASE_URL=http://localhost:8000`.
- E2E API URL is wrong: set `E2E_API_URL=http://localhost:8000`.
- E2E frontend URL is wrong: set `E2E_FRONTEND_URL=http://localhost:5173`.
- No manual demo alerts appear: start Redpanda, create topics, start the worker, and publish `defect-spike` events.
- Duplicate active investigation exists: use a fresh API-created alert fixture or resolve the existing investigation.
- AI summary looks generic: add richer alert evidence or run the full demo to create related defects, sensor readings, and station events.

Phase 14 can add one-command demo improvements later. Phase 13 keeps the test runner explicit.

## Git Commit

```bash
git commit -m "phase-13 end to end manufacturing quality workflow tests"
```
