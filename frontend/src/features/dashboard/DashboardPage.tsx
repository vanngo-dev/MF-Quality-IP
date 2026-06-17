import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatCard } from "../../components/ui/StatCard";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getAlerts } from "../../services/alertsApi";
import { getDefects } from "../../services/defectsApi";
import { getStations } from "../../services/stationsApi";
import { getVehicles } from "../../services/vehiclesApi";

export function DashboardPage() {
  const vehiclesQuery = useQuery({ queryKey: ["vehicles"], queryFn: getVehicles });
  const defectsQuery = useQuery({ queryKey: ["defects"], queryFn: getDefects });
  const alertsQuery = useQuery({ queryKey: ["alerts"], queryFn: getAlerts });
  const stationsQuery = useQuery({ queryKey: ["stations"], queryFn: getStations });

  const isLoading = vehiclesQuery.isLoading || defectsQuery.isLoading || alertsQuery.isLoading || stationsQuery.isLoading;
  const isError = vehiclesQuery.isError || defectsQuery.isError || alertsQuery.isError || stationsQuery.isError;

  if (isLoading) {
    return <LoadingState message="Loading dashboard metrics..." />;
  }

  if (isError) {
    return <ErrorState message="Unable to load dashboard data from the backend API." />;
  }

  const vehicles = vehiclesQuery.data ?? [];
  const defects = defectsQuery.data ?? [];
  const alerts = alertsQuery.data ?? [];
  const stations = stationsQuery.data ?? [];
  const openDefects = defects.filter((defect) => defect.status === "open");
  const openAlerts = alerts.filter((alert) => alert.status === "open");
  const criticalAlerts = alerts.filter((alert) => alert.severity === "critical");
  const topDefectStation = findTopDefectStation(defects, stations);
  const recentAlerts = alerts.slice(0, 5);

  return (
    <section className="page-stack">
      <PageHeader
        title="Dashboard"
        description="Live manufacturing quality summary from the FastAPI backend."
      />

      <div className="action-row">
        <button
          className="secondary-button"
          type="button"
          onClick={() => {
            void vehiclesQuery.refetch();
            void defectsQuery.refetch();
            void alertsQuery.refetch();
            void stationsQuery.refetch();
          }}
        >
          Refresh Data
        </button>
      </div>

      <div className="stat-grid">
        <StatCard title="Total Vehicles" value={String(vehicles.length)} description="Vehicles returned by the backend" />
        <StatCard title="Open Defects" value={String(openDefects.length)} description="Defects with open status" />
        <StatCard title="Open Alerts" value={String(openAlerts.length)} description="Alerts requiring quality review" />
        <StatCard title="Critical Alerts" value={String(criticalAlerts.length)} description="Critical severity alert count" />
        <StatCard title="Top Defect Station" value={topDefectStation} description="Calculated from live defect rows" />
        <StatCard title="Latest Sensor Event" value="Not available yet" description="Sensor detail API is not exposed yet" />
      </div>

      <DataTable
        caption="Latest alerts"
        columns={[
          { key: "code", header: "Alert Code", render: (row) => row.alert_code },
          { key: "title", header: "Title", render: (row) => row.title },
          { key: "station", header: "Station", render: (row) => stationLabel(row.station_id, stations) },
          { key: "severity", header: "Severity", render: (row) => <SeverityBadge severity={row.severity} /> },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
        ]}
        rows={recentAlerts}
      />
    </section>
  );
}

function findTopDefectStation(
  defects: { station_id: number }[],
  stations: { id: number; code: string }[],
) {
  if (defects.length === 0) {
    return "None";
  }

  const counts = defects.reduce<Record<number, number>>((accumulator, defect) => {
    accumulator[defect.station_id] = (accumulator[defect.station_id] ?? 0) + 1;
    return accumulator;
  }, {});
  const [stationId] = Object.entries(counts).sort(([, left], [, right]) => right - left)[0];

  return stationLabel(Number(stationId), stations);
}

function stationLabel(stationId: number, stations: { id: number; code: string }[]) {
  return stations.find((station) => station.id === stationId)?.code ?? `Station ${stationId}`;
}
