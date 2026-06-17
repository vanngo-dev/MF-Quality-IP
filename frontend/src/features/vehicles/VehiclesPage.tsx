import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getDefects } from "../../services/defectsApi";
import { getStations } from "../../services/stationsApi";
import { getVehicleByVin, getVehicles } from "../../services/vehiclesApi";

export function VehiclesPage() {
  const [vinSearch, setVinSearch] = useState("");
  const [selectedVin, setSelectedVin] = useState("");
  const vehiclesQuery = useQuery({ queryKey: ["vehicles"], queryFn: getVehicles });
  const defectsQuery = useQuery({ queryKey: ["defects"], queryFn: getDefects });
  const stationsQuery = useQuery({ queryKey: ["stations"], queryFn: getStations });
  const selectedVehicleQuery = useQuery({
    queryKey: ["vehicle", selectedVin],
    queryFn: () => getVehicleByVin(selectedVin),
    enabled: selectedVin.length > 0,
  });

  const vehicles = vehiclesQuery.data ?? [];
  const stations = stationsQuery.data ?? [];
  const filteredVehicles = useMemo(() => {
    const normalizedSearch = vinSearch.trim().toLowerCase();

    if (!normalizedSearch) {
      return vehicles;
    }

    return vehicles.filter((vehicle) => vehicle.vin.toLowerCase().includes(normalizedSearch));
  }, [vehicles, vinSearch]);
  const selectedVehicle = selectedVehicleQuery.data ?? vehicles.find((vehicle) => vehicle.vin === selectedVin);
  const selectedVehicleDefects = selectedVehicle
    ? (defectsQuery.data ?? []).filter((defect) => defect.vehicle_id === selectedVehicle.id)
    : [];

  if (vehiclesQuery.isLoading || defectsQuery.isLoading || stationsQuery.isLoading) {
    return <LoadingState message="Loading vehicles..." />;
  }

  if (vehiclesQuery.isError || defectsQuery.isError || stationsQuery.isError) {
    return <ErrorState message="Unable to load vehicle data from the backend API." />;
  }

  return (
    <section className="page-stack">
      <PageHeader title="Vehicles" description="Live vehicle list with VIN search and selected vehicle context." />

      <form
        className="filter-row"
        onSubmit={(event) => {
          event.preventDefault();
          setSelectedVin(vinSearch.trim());
        }}
      >
        <label>
          VIN Search
          <input
            type="search"
            value={vinSearch}
            onChange={(event) => setVinSearch(event.target.value)}
            placeholder="MQPLANT0000000001"
          />
        </label>
        <button className="secondary-button" type="submit">
          Search VIN
        </button>
      </form>

      <DataTable
        caption="Vehicles"
        columns={[
          { key: "vin", header: "VIN", render: (row) => row.vin },
          { key: "model", header: "Model", render: (row) => row.model },
          { key: "station", header: "Current Station", render: (row) => stationLabel(row.current_station_id, stations) },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.build_status} /> },
        ]}
        rows={filteredVehicles}
      />

      {selectedVin ? (
        <section className="detail-panel" aria-label="Selected vehicle details">
          {selectedVehicleQuery.isLoading ? <LoadingState message="Loading selected vehicle..." /> : null}
          {selectedVehicleQuery.isError ? <ErrorState message="Vehicle not found for the entered VIN." /> : null}
          {selectedVehicle ? (
            <>
              <h2>{selectedVehicle.vin}</h2>
              <dl className="detail-grid">
                <div>
                  <dt>Model</dt>
                  <dd>{selectedVehicle.model}</dd>
                </div>
                <div>
                  <dt>Model Year</dt>
                  <dd>{selectedVehicle.model_year}</dd>
                </div>
                <div>
                  <dt>Current Station</dt>
                  <dd>{stationLabel(selectedVehicle.current_station_id, stations)}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>
                    <StatusBadge status={selectedVehicle.build_status} />
                  </dd>
                </div>
              </dl>
              <DataTable
                caption="Defects for selected vehicle"
                columns={[
                  { key: "code", header: "Defect Code", render: (row) => row.defect_code },
                  { key: "severity", header: "Severity", render: (row) => <SeverityBadge severity={row.severity} /> },
                  { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
                  { key: "detected", header: "Detected", render: (row) => formatDate(row.detected_at) },
                ]}
                rows={selectedVehicleDefects}
              />
              <p className="placeholder-note">Station event history will be added in a later phase.</p>
            </>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}

function stationLabel(stationId: number | null, stations: { id: number; code: string }[]) {
  if (stationId === null) {
    return "Not assigned";
  }

  return stations.find((station) => station.id === stationId)?.code ?? `Station ${stationId}`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
