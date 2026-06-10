# YouTube Tutorial Notes

## Phase 1: Project Foundation and Health Checks

### Episode Goal

Build the first commit of a manufacturing quality intelligence platform that can boot locally, expose a backend health contract, render a frontend operational status screen, and run automated tests.

### Recording Outline

1. Introduce the platform idea: manufacturing defects, investigations, event ingestion, search, and AI summaries.
2. Show the empty repository and explain the phase-by-phase rule.
3. Create the FastAPI backend and `/health` endpoint.
4. Create the React + TypeScript + Vite frontend.
5. Connect the frontend to the backend health endpoint.
6. Add Docker Compose services for PostgreSQL, Redpanda, and Elasticsearch.
7. Add backend and frontend tests.
8. Add GitHub Actions CI.
9. Run the automated checks.
10. Commit Phase 1.

### Concepts to Explain

- A health endpoint is a simple contract that tells other tools whether the API is reachable.
- Docker Compose gives the project repeatable local infrastructure.
- Alembic migrations will track database schema changes in later phases.
- React Testing Library verifies what a user sees instead of testing implementation details.
- CI protects the portfolio project by running tests on every pull request.

### Demo Script

```bash
cd backend
../.venv/Scripts/python -m uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```

Open:

- http://localhost:8000/health
- http://localhost:5173

### Commit Message

```bash
git commit -m "Initialize project foundation and health checks"
```
