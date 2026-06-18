# Phase 15 — GitHub Actions CI Pipeline

## Goal

Add a GitHub Actions CI pipeline that validates the project when code is pushed to GitHub or a pull request is opened.

The FastAPI backend remains in `backend/`. This phase does not create an `api/` folder, does not change the Phase 14 demo workflow, and does not add Phase 16 portfolio polish.

## What Was Built

- Updated `.github/workflows/ci.yml`.
- Added CI triggers for pushes and pull requests targeting `main` and `master`.
- Added Docker Compose validation.
- Added backend tests.
- Added worker tests.
- Added event-generator tests.
- Added frontend tests and build.
- Documented CI behavior in README, testing strategy, tutorial notes, and this guide.

## Why This Matters

CI gives the project a professional safety net. Instead of relying on local memory, every push and pull request can prove that core services still install, test, and build.

For a manufacturing quality platform, this matters because the system spans multiple moving parts: backend APIs, a worker, event simulation, frontend UI, Docker Compose, and E2E workflows. CI catches regressions before they reach a demo branch.

## CI Workflow Overview

Workflow file:

```text
.github/workflows/ci.yml
```

Triggers:

```yaml
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
```

The workflow is intentionally readable and split into separate jobs. A failure in backend tests, worker tests, event-generator tests, frontend tests, or Compose validation points directly to the subsystem that needs attention.

## Jobs Added

CI jobs:

- `compose-validation`: validates Docker Compose with `docker compose config` and the optional `tools` profile.
- `backend-tests`: installs the backend package and runs `pytest`.
- `worker-tests`: installs the worker package and runs `pytest`.
- `event-generator-tests`: installs the event generator package and runs `pytest`.
- `frontend-tests`: runs `npm ci`, `npm run test:run`, and `npm run build`.

Playwright E2E is not added to CI in Phase 15. It remains local-only because it requires backend and frontend startup, seeded data, browser installation, and more orchestration than the core CI should carry right now.

## Environment Variables

CI uses safe defaults:

```text
AI_PROVIDER=mock
AI_SUMMARY_PROVIDER=mock
ELASTICSEARCH_URL=http://localhost:9200
KAFKA_BOOTSTRAP_SERVERS=localhost:19092
```

No OpenAI-compatible API key is required. AI summaries use the deterministic mock provider.

Backend tests use SQLite fixtures and mocked Elasticsearch behavior where needed, so CI does not start PostgreSQL or Elasticsearch service containers. Worker and event-generator tests do not require live Redpanda because Kafka behavior is mocked.

## Local Commands Matching CI

Compose validation:

```powershell
docker compose config
docker compose --profile tools config
```

Backend:

```powershell
cd backend
pip install -e .
pytest
```

Worker:

```powershell
cd worker
pip install -e .
pytest
```

Event generator:

```powershell
cd event-generator
pip install -e .
pytest
```

Frontend:

```powershell
cd frontend
npm ci
npm run test:run
npm run build
```

Makefile shortcut:

```powershell
make test
docker compose config
```

## How to Run It Locally

Run the same checks before pushing:

```powershell
docker compose config
docker compose --profile tools config
```

```powershell
cd backend
pytest
```

```powershell
cd ../worker
pytest
```

```powershell
cd ../event-generator
pytest
```

```powershell
cd ../frontend
npm run test:run
npm run build
```

If dependencies are missing, install them first:

```powershell
cd backend
pip install -e .
```

```powershell
cd worker
pip install -e .
```

```powershell
cd event-generator
pip install -e .
```

```powershell
cd frontend
npm ci
```

## How to Verify in GitHub

After pushing to GitHub:

1. Open the repository in GitHub.
2. Click the Actions tab.
3. Open the latest `CI` workflow run.
4. Confirm each job is green.
5. If a job fails, open the failing step and copy the exact command locally.

If the repository owner and name are known, update the README badge placeholder:

```markdown
![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)
```

## Automated Tests

Automated CI runs:

- Docker Compose config validation.
- Backend unit and API tests.
- Worker mapper, persistence, consumer, and rule-engine tests.
- Event-generator schema, scenario, routing, and producer tests.
- Frontend Vitest tests.
- Frontend TypeScript and Vite production build.

The CI does not use paid services, secrets, external AI APIs, or full Docker Compose application startup.

## Manual Tests

Manual checks after CI passes:

- Run `make demo` from Phase 14.
- Open `http://localhost:5173`.
- Confirm dashboard data loads.
- Produce defect-spike events.
- Confirm alerts appear after worker ingestion.
- Create an investigation.
- Generate an AI summary.
- Resolve the investigation.
- Run `make test-e2e` when backend and frontend are running.

## Expected Results

- `.github/workflows/ci.yml` exists.
- CI triggers on pushes and pull requests to `main` and `master`.
- Compose validation passes.
- Backend tests pass.
- Worker tests pass.
- Event-generator tests pass.
- Frontend tests pass.
- Frontend build passes.
- CI does not require OpenAI API keys or paid services.
- E2E remains documented as local-only for Phase 15.

## Common Errors and Fixes

- CI cannot find backend folder: confirm the workflow uses `working-directory: backend`.
- `pip install -e .` fails: confirm `pyproject.toml` exists in that package folder.
- Missing `pyproject.toml`: run the job from `backend/`, `worker/`, or `event-generator/`, not the repo root.
- Postgres service not ready: Phase 15 backend tests should not need Postgres; use SQLite fixtures unless a future test requires a service container.
- `DATABASE_URL` wrong in CI: avoid live database dependencies for current tests or set the job environment explicitly.
- Elasticsearch not running: current search tests use mocked services; only add Elasticsearch if future tests require it.
- Kafka or Redpanda not available in CI: worker and event-generator tests should use mocks for normal CI.
- `npm ci` fails because `package-lock.json` is missing: use `npm install` or add a lockfile. This repo has `frontend/package-lock.json`.
- Frontend test script missing: confirm `frontend/package.json` includes `test:run`.
- Playwright browsers not installed: E2E is local-only in Phase 15; run `npx playwright install` locally before `make test-e2e`.
- E2E too flaky for CI: keep it out of required CI until a stable service orchestration job exists.
- CI badge owner/repo placeholder not updated: replace `REPLACE_OWNER/REPLACE_REPO` after pushing to GitHub.

## Git Commit

```bash
git commit -m "phase-15 github actions ci pipeline"
```
