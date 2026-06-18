# Testing Strategy

## Phase 3 Coverage

Backend tests verify:

- Database configuration imports correctly.
- SQLAlchemy ORM models import correctly.
- Phase 1 health endpoints still pass.
- Seed data can be created.
- Read-only domain API endpoints return the expected seeded data.
- Vehicle lookup by VIN returns a vehicle.
- Unknown VIN lookup returns `404`.
- Defects can be created, listed, and fetched by ID.
- Defect validation rejects invalid vehicle IDs, station IDs, and severity values.
- Alerts can be created, listed, fetched by ID, and updated by status.
- Alert validation rejects invalid station IDs, severity values, and status values.
- Investigations can be created, listed, fetched by ID, and updated.
- Investigation validation rejects invalid alert IDs and status values.

## Phase 4 Event Generator Coverage

Event generator tests verify:

- Base event schema validates a valid event.
- Base event schema rejects missing `event_id`.
- Base event schema rejects invalid timestamps.
- Station event payloads validate.
- Sensor reading type and value validation works.
- Defect severity and defect code validation works.
- Deterministic generation returns the expected six events.
- Deterministic generation includes station, sensor, inspection, and defect events.
- Random generation respects the requested count.
- Random generation produces valid event schemas.
- Invalid random counts fail cleanly.
- CLI deterministic and random modes exit successfully.

## Phase 5 Streaming Producer Coverage

Producer tests verify:

- Phase 4 deterministic generation still works.
- Phase 4 random generation still works.
- Station events route to `station.events`.
- Sensor readings route to `sensor.readings`.
- Defect events route to `quality.defects`.
- Unknown event types fail clearly.
- Broker configuration loads from CLI input or `KAFKA_BOOTSTRAP_SERVERS`.
- Mock producer receives the expected topic and JSON payload.
- Publish mode validates events before publishing.
- Publish CLI deterministic and random modes exit successfully with the mock producer.

## Phase 6 Worker Consumer Coverage

Worker tests verify:

- Station events map to production event persistence data.
- Sensor reading events map to sensor reading persistence data.
- Defect events map to defect persistence data.
- Duplicate `event_id` values are ignored safely.
- Invalid station events are rejected and can be logged.
- Invalid sensor reading events are rejected and can be logged.
- Invalid defect events are rejected and can be logged.
- The persistence service saves a production event.
- The persistence service saves a sensor reading.
- The persistence service saves a defect.
- Worker configuration loads broker and database URL from environment variables.
- Consumer topic subscription configuration includes `station.events`, `sensor.readings`, and `quality.defects`.
- Kafka consumer setup is tested with a mocked Kafka module, not a live Redpanda broker.

See `docs/phase6.md` for the dedicated Phase 6 worker test and manual verification guide.

## Phase 7 Rule Engine Coverage

Rule engine tests verify:

- Repeated defects at the same station trigger `REPEATED_DEFECT_STATION`.
- Repeated defect station rule stays quiet below threshold.
- Equipment temperature readings above threshold trigger `EQUIPMENT_TEMPERATURE_HIGH`.
- Temperature readings below threshold do not trigger.
- Torque readings outside tolerance trigger `TORQUE_OUT_OF_TOLERANCE`.
- Torque readings inside tolerance do not trigger.
- Vision confidence below threshold triggers `VISION_CONFIDENCE_LOW`.
- Vision confidence above threshold does not trigger.
- Same-code defect spikes trigger `DEFECT_CODE_SPIKE`.
- Defect spike rule stays quiet below threshold.
- Consecutive inspection failures trigger `CONSECUTIVE_INSPECTION_FAILURES`.
- Mixed pass/fail inspection sequences do not trigger.
- Alert persistence works.
- Duplicate open alert prevention works.
- `quality.alerts` publish function is called when an alert is created.
- Rule engine can run after event persistence.
- Invalid or incomplete data does not crash the rule engine.

Event-generator tests verify `defect-spike` mode and mock publishing counts.

## Phase 8 Frontend Foundation Coverage

Frontend tests verify:

- App renders.
- Root route redirects to `/dashboard`.
- Dashboard route renders.
- Sidebar navigation renders.
- Sidebar contains Dashboard, Stations, Equipment, Vehicles, Defects, Alerts, and Investigations links.
- Sidebar navigation can move between routes.
- Dashboard displays mock stat cards.
- Status badges render supported labels.
- Severity badges render supported labels.
- Loading state renders.
- Error state renders.
- API client uses the configured base URL or default base URL.

Phase 8 tests do not require the backend API to be running because pages use mock/static data. Phase 9 replaces those placeholders with mocked live API responses in frontend tests.

## Phase 9 Frontend Data Integration Coverage

Frontend tests verify:

- API client functions build the correct backend URLs.
- Alert status updates call `PATCH /api/v1/alerts/{id}/status` with `status = acknowledged`.
- Dashboard renders loading state.
- Dashboard renders error state.
- Dashboard calculates live stats from mocked API responses.
- Stations page renders station rows from mocked API data.
- Equipment page renders equipment rows from mocked API data.
- Vehicles page renders the vehicle list.
- VIN search fetches and displays selected vehicle details.
- Defects page renders defect rows from mocked API data.
- Defects page filters by severity.
- Defects page filters by status.
- Alerts page renders alert rows from mocked API data.
- Alerts page filters by severity.
- Alerts page filters by status.
- Alert acknowledgement uses a TanStack Query mutation.
- Investigations page renders investigation rows from mocked API data.

Frontend automated tests mock `fetch`, so they do not require the backend API, PostgreSQL, Redpanda, or the worker to be running.

## Phase 10 Search Coverage

Backend search tests verify:

- Search endpoint rejects an empty query with `400`.
- Grouped search returns `defects`, `alerts`, `investigations`, and `events`.
- Defects search returns a matching defect result.
- Alerts search returns a matching alert result.
- Investigations search returns a matching investigation result.
- No results return empty groups.
- Search service builds Elasticsearch multi-match queries.
- Search service parses Elasticsearch hits into stable API results.
- Missing Elasticsearch indexes return empty result lists.
- Indexer builds valid defect documents.
- Indexer builds valid alert documents.
- Indexer builds valid investigation documents.
- Indexer builds valid event summary documents.
- Reindex command handles an empty database.

Frontend search tests verify:

- Search page renders.
- Search input accepts text.
- Submitting search calls the backend API client.
- Loading state appears while search is pending.
- Error state appears when search fails.
- Grouped results render.
- No results message renders.
- Sidebar includes the Search link.

Normal automated tests use mocked Elasticsearch and mocked frontend `fetch`. They do not require a live Elasticsearch container.

## Phase 11 Investigation Workflow Coverage

Backend tests verify:

- Create investigation from alert succeeds.
- Creating from a missing alert returns `404`.
- Creating from an alert updates alert status to `investigating`.
- Duplicate active investigation creation for the same alert returns `409`.
- Investigation summary updates successfully.
- Root-cause hypothesis updates successfully.
- Investigation status endpoint updates status successfully.
- Invalid investigation status returns validation failure.
- Resolving an investigation sets `closed_at`.
- Resolving an investigation updates the related alert to `resolved`.
- Investigation detail returns `evidence_json`.
- Alert detail still returns alert evidence.

Frontend tests verify:

- Alert detail page renders alert data.
- Alert detail page renders evidence.
- Create investigation form renders.
- Create investigation mutation calls the expected backend endpoint.
- Investigation detail page renders investigation data.
- Investigation form updates summary.
- Investigation form updates root-cause hypothesis.
- Investigation status update calls the status endpoint.
- Evidence panel renders JSON evidence.
- Timeline panel renders timeline items.
- Search result links route to alert detail.

Frontend workflow tests mock API responses. They do not require a running backend for normal automated runs.

## Phase 12 AI Summary Coverage

Backend tests verify:

- Mock provider returns structured summary content.
- Mock provider uses alert evidence.
- Mock provider uses defect evidence.
- Mock provider uses sensor evidence.
- Missing evidence returns limitations.
- Minimal evidence does not produce invented root-cause claims.
- Confidence is low when evidence is thin.
- Confidence is medium when multiple evidence sources agree.
- Default provider is mock and does not require external network calls.
- `POST /api/v1/investigations/{id}/ai-summary` succeeds.
- Missing investigation returns `404`.
- Summary is saved to the investigation.
- `updated_at` changes after summary generation.

Frontend tests verify:

- Investigation detail page shows Generate AI Summary.
- Clicking the button calls the AI summary mutation.
- Loading state appears while generating.
- AI Summary panel renders likely issue.
- AI Summary panel renders evidence list.
- AI Summary panel renders recommended next checks.
- AI Summary panel renders confidence.
- AI Summary panel renders limitations.
- Error state appears if generation fails.
- Existing saved `ai_summary` displays and can be regenerated.

Tests use the mock provider and mocked frontend API responses. No OpenAI-compatible API key or external API call is required.

## Phase 13 End-to-End Coverage

Phase 13 adds Playwright browser coverage for the complete manufacturing quality workflow. Unit tests still verify small functions and components in isolation. Integration tests still verify backend API behavior and frontend API calls with mocked responses. E2E tests verify that the running backend and running frontend work together through the same UI path a quality engineer would use.

Playwright E2E tests verify:

- Playwright configuration loads with the expected frontend base URL.
- The browser can reach the frontend at `http://localhost:5173`.
- The Playwright API client can reach backend health at `http://localhost:8000/health`.
- API-created alert fixtures appear in the Alerts page.
- Alert detail pages load.
- Investigation creation from an alert works.
- Investigation detail pages load after creation.
- AI summary generation works.
- The summary panel shows likely issue, evidence, recommended next checks, confidence, and limitations.
- Investigation resolution works and the resolved status appears.

The E2E suite creates fixture alerts through the FastAPI API before driving the browser. API-created fixtures are stable because they do not depend on previous local demo runs, Redpanda timing, worker timing, or whatever records happen to exist in PostgreSQL. The manual demo still uses the full event-generator to Redpanda to worker to database to UI flow.

## Local Test Command

Backend:

```powershell
cd backend
pytest
```

Event generator:

```powershell
cd event-generator
pip install -e .
pytest
```

Worker:

```powershell
cd worker
pip install -e .
pytest
```

Frontend:

```powershell
cd frontend
npm install
npm run test
npm run build
```

End-to-end:

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

E2E environment defaults:

```text
E2E_FRONTEND_URL=http://localhost:5173
E2E_API_URL=http://localhost:8000
```

If editable install is not available:

```powershell
pip install pydantic pytest kafka-python-ng sqlalchemy psycopg2-binary
```

Phase 5 uses `kafka-python-ng` for the real producer. Phase 6 uses the same `kafka-python-ng` client for the worker consumer.

```powershell
pip install pydantic pytest kafka-python-ng
```

## Database Test Approach

Tests use SQLAlchemy with an in-memory SQLite database. This keeps the tests fast and independent of Docker while still exercising the same ORM models, seed function, and FastAPI dependency injection path.

PostgreSQL is still the application database for local development and demos:

```powershell
docker compose up postgres
cd backend
alembic upgrade head
python -m app.db.seed
```

## Manual Verification

After seeding PostgreSQL and starting the API, call the `/api/v1` endpoints with `curl` and confirm the seeded counts:

- 1 plant
- 2 lines
- 6 stations
- 8 equipment records
- 10 vehicles

Then create one defect, one alert, and one investigation. Confirm invalid IDs return `404` and invalid status or severity values return `422`.

## Streaming Manual Verification

Automated streaming tests use a mock producer so Redpanda is not required for normal test runs.

Manual streaming verification uses Redpanda:

```powershell
docker compose up redpanda redpanda-console
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

Then verify with Redpanda Console at http://localhost:8080 or with:

```powershell
docker compose exec redpanda rpk topic consume station.events --num 5
docker compose exec redpanda rpk topic consume sensor.readings --num 5
docker compose exec redpanda rpk topic consume quality.defects --num 5
```

## Worker Manual Verification

Automated worker tests do not require Redpanda or PostgreSQL. Manual verification uses both services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed data:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start the worker in another terminal:

```powershell
cd worker
pip install -e .
python -m app.main
```

Produce demo events in another terminal:

```powershell
cd event-generator
python -m app.main --mode deterministic --publish --broker localhost:19092
```

Verify API and database state:

```powershell
curl http://localhost:8000/api/v1/defects
curl http://localhost:8000/api/v1/stations
curl http://localhost:8000/api/v1/vehicles
docker compose exec postgres psql -U quality -d quality
```

```sql
select count(*) from production_events;
select count(*) from sensor_readings;
select count(*) from defects;
```

Expected results:

- Redpanda starts.
- PostgreSQL starts.
- Worker starts without crashing.
- Event generator publishes events.
- Worker consumes events.
- Production events are persisted.
- Sensor readings are persisted.
- Defects are persisted.
- Duplicate event IDs do not create duplicate rows.
- Invalid events are logged and skipped.
- In Phase 6 alone, no quality alerts are generated; Phase 7 adds alert rules after this ingestion flow.

## Rule Engine Manual Verification

Phase 7 manual verification uses the same Redpanda and PostgreSQL services:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed data:

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Create topics:

```powershell
docker compose exec redpanda rpk topic create station.events sensor.readings quality.defects quality.alerts investigation.events
docker compose exec redpanda rpk topic list
```

Start the worker:

```powershell
cd worker
pip install -e .
python -m app.main
```

Produce deterministic defect spike events:

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Verify alerts:

```powershell
curl http://localhost:8000/api/v1/alerts
docker compose exec redpanda rpk topic consume quality.alerts --num 5
```

Expected results:

- Worker persists defect and sensor events.
- Rule engine evaluates persisted data.
- At least one `quality_alerts` row is created.
- The alert is visible through `/api/v1/alerts`.
- `quality.alerts` receives an alert event.
- Running the same defect spike twice does not create duplicate open alerts for the same condition.

See `docs/phase7.md` for the dedicated Phase 7 guide.

## Frontend Manual Verification

Phase 9 manual verification:

```powershell
docker compose up postgres redpanda redpanda-console
```

Run migrations and seed data:

```powershell
cd backend
alembic upgrade head
python -m app.db.seed
```

Start the backend API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Optionally start the worker and produce demo alerts:

```powershell
cd worker
python -m app.main
```

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

Expected results:

- Dashboard page loads.
- Sidebar appears.
- Navigation links work.
- Dashboard displays live backend metrics.
- Stations page loads real station data.
- Equipment page loads real equipment data.
- Vehicles page loads real vehicle data.
- VIN search works.
- Defects page loads real defect data.
- Defect filters work.
- Alerts page loads real alert data.
- Alert filters work.
- Acknowledge alert updates alert status.
- Investigations page loads real investigation data.
- Loading states appear while API calls are pending.
- Error states appear if the backend is stopped.
- No browser console errors.

The backend must be running for the Phase 9 browser demo. The frontend automated tests still mock API responses.

See `docs/phase9.md` for the dedicated Phase 9 guide.

## Search Manual Verification

Start services:

```powershell
docker compose up postgres elasticsearch
```

If using streamed demo data:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

Run backend setup:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
```

Run reindex:

```powershell
python -m app.search.reindex
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Test backend search:

```powershell
curl "http://localhost:8000/api/v1/search?q=torque"
curl "http://localhost:8000/api/v1/search/defects?q=torque"
curl "http://localhost:8000/api/v1/search/alerts?q=defect"
curl "http://localhost:8000/api/v1/search/investigations?q=root"
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
http://localhost:5173/search
```

Expected results:

- Elasticsearch starts on port 9200.
- Reindex command prints counts for defects, alerts, investigations, and events.
- Search endpoints return grouped or specialized results.
- Search page loads.
- Search input works.
- No results message appears for a nonsense query.
- Error state appears if backend or Elasticsearch is stopped.

See `docs/phase10.md` for the dedicated Phase 10 guide.

## Investigation Workflow Manual Verification

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

Create alert data if needed with the existing API or Phase 7 event flow.

Start the frontend:

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

Expected workflow:

- Open an alert.
- Review structured evidence.
- Create an investigation.
- Confirm alert status changes to investigating.
- Open the investigation detail page.
- Update summary and root-cause hypothesis.
- Change investigation status.
- Resolve the investigation.
- Confirm the related alert is resolved.

See `docs/phase11.md` for the dedicated Phase 11 guide.

## AI Summary Manual Verification

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

Generate a summary by API:

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

Expected workflow:

- Open an investigation detail page.
- Click Generate AI Summary.
- Confirm loading appears.
- Confirm likely issue, evidence, next checks, confidence, and limitations appear.
- Refresh the page and confirm the saved summary still appears.

See `docs/phase12.md` for the dedicated Phase 12 guide.

## End-to-End Manual Verification

Automated E2E verification expects the backend and frontend to be running. Start the API:

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

Start the frontend:

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

Manual full-system demo:

```powershell
docker compose up postgres redpanda redpanda-console elasticsearch
```

```powershell
cd backend
pip install -e .
alembic upgrade head
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

```powershell
cd worker
pip install -e .
python -m app.main
```

```powershell
cd event-generator
python -m app.main --mode defect-spike --publish --broker localhost:19092
```

Then open `http://localhost:5173/alerts`, create an investigation from an alert, generate the AI summary, and resolve the investigation.

Playwright stores screenshots, traces, and videos for failed or retried tests under `e2e/test-results/`. The HTML report is written to `e2e/playwright-report/`.

See `docs/phase13.md` for the dedicated Phase 13 guide.
