# Data Model

## Phase 6 Domain Model

The database stores stable manufacturing context, quality workflow records, and persisted event-ingestion records from Redpanda.

## Tables

| Table | Purpose |
| --- | --- |
| `plants` | Manufacturing sites, such as one assembly plant. |
| `production_lines` | Production lines inside a plant. |
| `stations` | Ordered work or inspection stations on a line. |
| `equipment` | Tools, robots, scanners, cameras, and testers installed at stations. |
| `vehicles` | Vehicles moving through the manufacturing process. |
| `production_events` | Timestamped events emitted as a vehicle moves through stations. |
| `sensor_readings` | Measurements from station equipment. |
| `defects` | Quality issues found on a vehicle at a station, optionally tied to equipment. |
| `quality_alerts` | Operational alerts raised from repeated defects, station evidence, or quality rules. |
| `investigations` | Engineering root-cause workflow records opened from alerts. |

## Relationships

- A plant has many production lines.
- A production line has many stations and vehicles.
- A station has many equipment records.
- A vehicle can have production events and defects.
- Equipment can have sensor readings.
- Sensor readings can also reference the station where the reading was captured.
- A defect references one vehicle and one station.
- A defect may reference one equipment record.
- An alert references one station and may reference one equipment record.
- An alert stores evidence in `evidence_json`.
- An investigation references one alert and stores root-cause notes and evidence.

## Quality Workflow Concepts

Defects represent specific product quality problems, such as a torque value below threshold on a vehicle.

Quality alerts represent workflow-level signals, such as repeated defects at the same station in a short time window. Alerts connect to evidence through the `evidence_json` field.

Investigations represent the engineering follow-up process. They capture summaries, root-cause hypotheses, evidence, and status changes while a quality team works toward containment or resolution.

Validation protects data integrity by rejecting invalid severity values, invalid status values, and references to vehicles, stations, equipment, or alerts that do not exist.

## Event Persistence Columns

Phase 6 adds ingestion metadata to the persisted event tables:

| Table | Ingestion columns |
| --- | --- |
| `production_events` | `event_id`, `created_at` |
| `sensor_readings` | `event_id`, `station_id`, `created_at` |
| `defects` | `event_id`, `created_at` |

`event_id` is unique per ingested event table and is checked by the worker before inserts. This makes event persistence idempotent: duplicate Redpanda messages are skipped instead of being stored twice.

The worker maps event timestamps into the existing database timestamp columns:

| Event field | Database column |
| --- | --- |
| Station `event_timestamp` | `production_events.occurred_at` |
| Sensor `event_timestamp` | `sensor_readings.recorded_at` |
| Defect `event_timestamp` | `defects.detected_at` |

Station event payloads are stored as JSON in `production_events.payload`. Sensor reading payload fields become typed columns: `reading_type` maps to `metric_name`, `reading_value` maps to `value`, and `unit` maps to `unit`.

## Worker Foreign Key Resolution

The worker keeps event consumption separate from the FastAPI API layer. It resolves event references to existing seeded domain rows before inserting:

- Vehicles by payload `vin`, then deterministic UUID suffix.
- Stations by payload `station_code`, then deterministic UUID suffix.
- Equipment by payload `equipment_code`, then deterministic UUID suffix.

If a referenced row cannot be resolved, the event is logged and skipped. The worker does not create missing vehicles, stations, or equipment during Phase 6.

## Rule-Based Alerts

Phase 7 creates `quality_alerts` from deterministic worker rules. Alerts are generated from persisted defects, sensor readings, and production events.

Rules write these existing alert fields:

| Column | Purpose |
| --- | --- |
| `alert_code` | Stable code for the rule that triggered. |
| `station_id` | Station where the risk was detected. |
| `equipment_id` | Equipment involved, when the rule is equipment-specific. |
| `severity` | `medium`, `high`, or `critical`. |
| `title` | Short operator-facing alert title. |
| `description` | Human-readable explanation. |
| `evidence_json` | Structured facts used by engineering investigations. |
| `status` | Defaults to `open`. |
| `created_at` | Alert creation timestamp. |

`evidence_json` stores rule-specific facts such as defect counts, sensor reading values, thresholds, time windows, station codes, and equipment codes. This keeps alerts explainable and makes later investigation workflows easier.

## Duplicate Alert Prevention

The worker does not create a duplicate open alert when an open alert already exists with the same:

- `alert_code`
- `station_id`
- `equipment_id`

This simple prevention keeps repeated polling, Redpanda redelivery, or repeated deterministic demos from flooding the `quality_alerts` table with the same active condition.

## Phase 7 Boundary

Phase 7 adds deterministic alert generation only. Frontend dashboards start in Phase 8. AI summaries and machine learning are intentionally not part of this phase.

## Phase 10 Search Documents

Phase 10 does not add new relational tables. PostgreSQL remains the system of record, while Elasticsearch stores denormalized search documents for fast free-text lookup.

An Elasticsearch index is a searchable collection of documents. A search document is a JSON representation of a database record plus useful lookup fields from related records, such as VIN, station code, and equipment code.

Indexes:

| Index | Source |
| --- | --- |
| `manufacturing-defects` | `defects` rows enriched with vehicle, station, and equipment fields. |
| `manufacturing-alerts` | `quality_alerts` rows enriched with station and equipment fields. |
| `manufacturing-investigations` | `investigations` rows with investigation text fields. |
| `manufacturing-events` | `production_events` rows enriched with vehicle and station fields. |

Defect search documents include:

- `id`
- `defect_code`
- `vehicle_id`
- `vin`
- `station_id`
- `station_code`
- `equipment_id`
- `equipment_code`
- `severity`
- `status`
- `description`
- `detected_at`
- `created_at`
- `type = defect`

Alert search documents include alert code, station and equipment references, severity, status, title, description, evidence JSON, creation time, and `type = alert`.

Investigation search documents include alert ID, title, summary, root-cause hypothesis, status, created/opened time, updated time, `ai_summary` set to `null` until Phase 12, and `type = investigation`.

Event summary documents include event ID, event type, vehicle and station references, payload JSON, event timestamp, and `type = event`.

Reindexing rebuilds these documents from PostgreSQL:

```powershell
cd backend
python -m app.search.reindex
```

Advanced filters are intentionally deferred. The full investigation lifecycle workflow starts in Phase 11, and AI summaries start in Phase 12.

## Phase 11 Investigation Workflow State

Phase 11 uses the existing `quality_alerts` and `investigations` tables.

Alerts can move through:

- `open`
- `acknowledged`
- `investigating`
- `resolved`

Investigations can move through:

- `draft`
- `active`
- `waiting_on_data`
- `resolved`

Creating an investigation from an alert:

- requires the alert to exist
- links the investigation through `alert_id`
- copies `quality_alerts.evidence_json` into `investigations.evidence_json`
- sets the alert to `investigating` when the alert was `open` or `acknowledged`
- rejects duplicate active investigations for the same alert

Investigation evidence matters because it preserves the structured facts that triggered the alert. Engineers can then add `summary` notes and a `root_cause_hypothesis` while they work toward containment or resolution.

Updating an investigation refreshes `updated_at`. Resolving an investigation sets `closed_at` and resolves the related alert.

Before Phase 12, `ai_summary` was exposed as a placeholder. Phase 12 persists generated structured summaries in the investigation record.

## Phase 12 AI Summary Persistence

Phase 12 adds a nullable JSON field:

| Table | Column | Purpose |
| --- | --- | --- |
| `investigations` | `ai_summary` | Persisted structured AI-assisted summary generated from available platform evidence. |

The saved summary contains:

- likely issue
- affected station
- affected equipment
- evidence list
- recommended next checks
- confidence
- limitations

The summary is generated from existing records only:

- linked alert details
- alert `evidence_json`
- related defects
- related sensor readings
- related station events
- investigation notes
- root-cause hypothesis
- investigation `evidence_json`

AI is treated as an assistant, not an authority. The stored summary must include limitations and avoid invented root-cause claims.

## Seed Data

The seed command creates a small demo plant:

- 1 plant: `PLT-DET`
- 2 production lines: `LINE-A`, `LINE-B`
- 6 stations
- 8 equipment records
- 10 vehicles with VINs starting at `MQPLANT0000000001`

Run it with:

```powershell
cd backend
python -m app.db.seed
```
