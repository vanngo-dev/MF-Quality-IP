# Data Model

## Phase 3 Domain Model

The database stores stable manufacturing context and the first quality workflow records.

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
