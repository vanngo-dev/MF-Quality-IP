# Phase 8 — React Frontend Foundation

## Goal

Create the React + TypeScript frontend foundation with routing, API client structure, layout, reusable UI components, a basic dashboard shell, and frontend test setup.

## What Was Built

Phase 8 updates the existing `frontend/` Vite app into an internal manufacturing quality dashboard shell.

It adds:

- React Router routes for dashboard, stations, equipment, vehicles, defects, alerts, and investigations
- TanStack Query setup for future server-state integration
- application layout with sidebar navigation and main content area
- reusable UI components for page headers, stat cards, tables, badges, loading states, and error states
- mock/static page content for the dashboard and operational queues
- API client service files for Phase 9 live backend data
- Vitest and React Testing Library tests for routing, layout, badges, states, dashboard cards, and API base URL behavior

## Why This Matters for Manufacturing Quality

Manufacturing quality teams need a focused operational interface for stations, vehicles, defects, alerts, and investigations. A dashboard shell gives the project a usable frontend structure before live data is connected.

React + TypeScript helps keep UI state, route definitions, component props, and API response types explicit. Reusable components keep status labels, severity labels, tables, and page structure consistent across quality workflows.

## Frontend Architecture

The frontend remains separate from the FastAPI backend:

```text
frontend React app -> API client foundation -> FastAPI backend routes
```

Phase 8 does not require the backend to be running. Pages use mock/static data so the dashboard shell can be tested independently.

TanStack Query is configured now so Phase 9 can connect live backend data without reworking the app foundation.

## Routes Added

- `/dashboard`
- `/stations`
- `/equipment`
- `/vehicles`
- `/defects`
- `/alerts`
- `/investigations`

The root route redirects to `/dashboard`.

## Components Added

- `AppLayout`
- `Sidebar`
- `PageHeader`
- `StatCard`
- `DataTable`
- `StatusBadge`
- `SeverityBadge`
- `LoadingState`
- `ErrorState`

## API Client Foundation

The API client reads:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Service files exist for:

- health
- stations
- equipment
- vehicles
- defects
- alerts
- investigations

Phase 8 prepares these services but does not wire pages to live backend data. Phase 9 will connect the routes to real API responses.

## How to Run It

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

Run:

```powershell
cd frontend
npm run test
```

Tests cover:

- app rendering
- dashboard route rendering
- sidebar navigation rendering
- required sidebar links
- dashboard mock stat cards
- status badges
- severity badges
- loading state
- error state
- API base URL default behavior

## Manual Tests

1. Start the frontend dev server.
2. Open `http://localhost:5173`.
3. Confirm the dashboard page loads.
4. Confirm the sidebar appears.
5. Click each navigation link.
6. Confirm each route loads without crashing.
7. Confirm status and severity badges render in tables.
8. Confirm there are no browser console errors.

The backend API is not required for the Phase 8 manual demo.

## Expected Results

- React app runs in Vite.
- Sidebar navigation works.
- `/` redirects to `/dashboard`.
- All required routes render.
- Dashboard displays mock stat cards.
- Placeholder tables render for domain pages.
- API client foundation exists.
- Tests pass in a normal local environment.

## Common Errors and Fixes

### Node.js not installed

Install Node.js 20 or newer, then rerun:

```powershell
cd frontend
npm install
```

### npm install fails

Delete `node_modules` if needed and rerun:

```powershell
npm install
```

### Port 5173 already in use

Stop the existing dev server or run Vite on another port:

```powershell
npm run dev -- --port 5174
```

### Vite dev server starts but page is blank

Check the browser console and terminal output. Most blank screens are caused by a TypeScript import error or a failed route render.

### React Router route not found

Use one of the configured routes or start at:

```text
http://localhost:5173/dashboard
```

### Vitest cannot find jsdom

Install dependencies:

```powershell
npm install
```

### Testing Library import errors

Confirm `src/setupTests.ts` imports `@testing-library/jest-dom/vitest`, then rerun:

```powershell
npm run test
```

### Environment variable VITE_API_BASE_URL missing

Phase 8 falls back to:

```text
http://localhost:8000
```

Create `frontend/.env` from `.env.example` if you need a different API URL.

### Backend not running, but Phase 8 should still work with placeholders

This is expected. Phase 8 uses mock/static data and does not require the backend. Phase 9 connects live backend data.

## Git Commit

```bash
git add .
git commit -m "phase-8 react frontend foundation"
```
