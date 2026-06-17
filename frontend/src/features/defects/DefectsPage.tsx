import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getDefects } from "../../services/defectsApi";
import { getEquipment } from "../../services/equipmentApi";
import { getStations } from "../../services/stationsApi";
import { getVehicles } from "../../services/vehiclesApi";

export function DefectsPage() {
  const [severityFilter, setSeverityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const defectsQuery = useQuery({ queryKey: ["defects"], queryFn: getDefects });
  const vehiclesQuery = useQuery({ queryKey: ["vehicles"], queryFn: getVehicles });
  const stationsQuery = useQuery({ queryKey: ["stations"], queryFn: getStations });
  const equipmentQuery = useQuery({ queryKey: ["equipment"], queryFn: getEquipment });
  const filteredDefects = useMemo(() => {
    return (defectsQuery.data ?? []).filter((defect) => {
      const matchesSeverity = severityFilter === "all" || defect.severity === severityFilter;
      const matchesStatus = statusFilter === "all" || defect.status === statusFilter;

      return matchesSeverity && matchesStatus;
    });
  }, [defectsQuery.data, severityFilter, statusFilter]);

  if (defectsQuery.isLoading || vehiclesQuery.isLoading || stationsQuery.isLoading || equipmentQuery.isLoading) {
    return <LoadingState message="Loading defects..." />;
  }

  if (defectsQuery.isError || vehiclesQuery.isError || stationsQuery.isError || equipmentQuery.isError) {
    return <ErrorState message="Unable to load defect data from the backend API." />;
  }

  const vehicles = vehiclesQuery.data ?? [];
  const stations = stationsQuery.data ?? [];
  const equipment = equipmentQuery.data ?? [];

  return (
    <section className="page-stack">
      <PageHeader title="Defects" description="Live defect queue with severity and status filters." />
      <div className="filter-row">
        <label>
          Severity
          <select value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)}>
            <option value="all">All severities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </label>
        <label>
          Status
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="all">All statuses</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="contained">Contained</option>
            <option value="resolved">Resolved</option>
          </select>
        </label>
      </div>
      <DataTable
        caption="Defects"
        columns={[
          { key: "code", header: "Defect Code", render: (row) => row.defect_code },
          { key: "vehicle", header: "Vehicle", render: (row) => vehicleLabel(row.vehicle_id, vehicles) },
          { key: "station", header: "Station", render: (row) => stationLabel(row.station_id, stations) },
          { key: "equipment", header: "Equipment", render: (row) => equipmentLabel(row.equipment_id, equipment) },
          { key: "severity", header: "Severity", render: (row) => <SeverityBadge severity={row.severity} /> },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
          { key: "detected", header: "Detected", render: (row) => formatDate(row.detected_at) },
          { key: "description", header: "Description", render: (row) => row.description },
        ]}
        rows={filteredDefects}
      />
    </section>
  );
}

function vehicleLabel(vehicleId: number, vehicles: { id: number; vin: string }[]) {
  return vehicles.find((vehicle) => vehicle.id === vehicleId)?.vin ?? `Vehicle ${vehicleId}`;
}

function stationLabel(stationId: number, stations: { id: number; code: string }[]) {
  return stations.find((station) => station.id === stationId)?.code ?? `Station ${stationId}`;
}

function equipmentLabel(equipmentId: number | null, equipment: { id: number; asset_tag: string }[]) {
  if (equipmentId === null) {
    return "Not specified";
  }

  return equipment.find((item) => item.id === equipmentId)?.asset_tag ?? `Equipment ${equipmentId}`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
