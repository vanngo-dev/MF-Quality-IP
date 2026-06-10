# Phase 1: Project Foundation and Health Checks

## Goal

Create the smallest working full-stack foundation for the Manufacturing Quality Intelligence Platform.

## What This Phase Establishes

- A FastAPI backend with a stable `/health` response.
- A React + TypeScript frontend that reads and displays backend health.
- Local infrastructure definitions for PostgreSQL, Redpanda, and Elasticsearch.
- Alembic scaffolding for future database migrations.
- Automated tests for backend and frontend health behavior.
- GitHub Actions CI that runs the same core checks.

## Why It Matters

Manufacturing quality systems depend on trustworthy operational signals. Before adding defect ingestion, event streaming, quality workflows, search, or AI summaries, the platform needs a simple way to prove that the frontend, backend, and local services are wired in the expected shape.

## Run Backend

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Visit:

- http://localhost:8000/health
- http://localhost:8000/docs

## Run Frontend

```powershell
cd frontend
npm run dev
```

Visit:

- http://localhost:5173

## Run Local Services

```powershell
docker compose up -d postgres redpanda elasticsearch
```

## Automated Checks

```powershell
cd backend
pytest
```

```powershell
cd frontend
npm run test
npm run build
```

```powershell
docker compose config
```

## Manual Test Steps

1. Start the backend.
2. Open http://localhost:8000/health.
3. Confirm the response status is `ok`.
4. Start the frontend.
5. Open http://localhost:5173.
6. Confirm the API Health tile shows `Operational`.
7. Stop the backend and refresh the frontend.
8. Confirm the API Health tile shows `Unavailable`.

## Troubleshooting

- If `fastapi` cannot be imported, install backend dependencies from `backend/requirements.txt` and `backend/requirements-dev.txt`.
- If `python -m venv .venv` fails during `ensurepip` on Windows, create a workspace temp folder and retry with `TEMP` and `TMP` pointed at that folder.
- If `npm run dev` fails, run `npm install` inside `frontend`.
- If the frontend cannot reach the API, confirm the backend is running on port `8000`.
- If Docker services fail to start, check whether ports `5432`, `9092`, or `9200` are already in use.
- If package installation fails locally, confirm network access to PyPI and the npm registry.
- If Git reports `dubious ownership`, run `git config --global --add safe.directory D:/MyApps/MF-Quality-IP` or use `git -c safe.directory=D:/MyApps/MF-Quality-IP <command>`.
