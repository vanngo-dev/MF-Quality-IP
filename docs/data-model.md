# Data Model

## Phase 2 Domain Model

The Phase 2 database stores the stable manufacturing context that later quality workflows will use.

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
| `defects` | Quality issues found on a vehicle at a station. |
| `quality_alerts` | Alerts raised from defects or quality rules. |
| `investigations` | Human or AI-assisted investigation records for defects. |

## Relationships

- A plant has many production lines.
- A production line has many stations and vehicles.
- A station has many equipment records.
- A vehicle can have production events and defects.
- Equipment can have sensor readings.
- A defect can have quality alerts and investigations.

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
