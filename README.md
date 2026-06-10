# Manufacturing Quality Intelligence Platform

Full-stack portfolio project for manufacturing quality workflows, event-driven ingestion, investigation summaries, and operational dashboards.

## Current Phase

Phase 1 establishes the project foundation:

- FastAPI backend with a health contract.
- React + TypeScript + Vite frontend status surface.
- PostgreSQL, Redpanda, and Elasticsearch local services through Docker Compose.
- Backend and frontend automated tests.
- GitHub Actions CI for backend and frontend checks.
- Documentation and YouTube tutorial notes.

## Repository Structure

```text
backend/              FastAPI application and backend tests
frontend/             React, TypeScript, and Vite application
docs/                 Phase notes and tutorial notes
.github/workflows/    GitHub Actions CI
docker-compose.yml    Local platform services
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop

## Backend

```bash
cd backend
python -m venv ../.venv
../.venv/Scripts/python -m pip install -r requirements.txt -r requirements-dev.txt
../.venv/Scripts/python -m uvicorn app.main:app --reload
```

Backend API:

- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend app:

- http://localhost:5173

## Local Services

```bash
docker compose up -d postgres redpanda elasticsearch
```

Services:

- PostgreSQL: localhost:5432
- Redpanda: localhost:9092
- Elasticsearch: http://localhost:9200

## Tests

Backend:

```bash
cd backend
../.venv/Scripts/python -m pytest
```

Frontend:

```bash
cd frontend
npm run test
npm run build
```

Docker Compose syntax:

```bash
docker compose config
```
