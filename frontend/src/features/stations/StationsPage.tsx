import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { getAlerts } from "../../services/alertsApi";
import { getDefects } from "../../services/defectsApi";
import { getStations } from "../../services/stationsApi";

export function StationsPage() {
  const stationsQuery = useQuery({ queryKey: ["stations"], queryFn: getStations });
  const defectsQuery = useQuery({ queryKey: ["defects"], queryFn: getDefects });
  const alertsQuery = useQuery({ queryKey: ["alerts"], queryFn: getAlerts });

  if (stationsQuery.isLoading || defectsQuery.isLoading || alertsQuery.isLoading) {
    return <LoadingState message="Loading stations..." />;
  }

  if (stationsQuery.isError || defectsQuery.isError || alertsQuery.isError) {
    return <ErrorState message="Unable to load station data from the backend API." />;
  }

  const defects = defectsQuery.data ?? [];
  const alerts = alertsQuery.data ?? [];

  return (
    <section className="page-stack">
      <PageHeader title="Stations" description="Live station list with client-side defect and alert counts." />
      <DataTable
        caption="Stations"
        columns={[
          { key: "code", header: "Code", render: (row) => row.code },
          { key: "name", header: "Name", render: (row) => row.name },
          { key: "type", header: "Type", render: () => "Workstation" },
          { key: "line", header: "Line", render: (row) => `Line ${row.line_id}` },
          { key: "defects", header: "Defects", render: (row) => countByStation(defects, row.id) },
          { key: "alerts", header: "Alerts", render: (row) => countByStation(alerts, row.id) },
        ]}
        rows={stationsQuery.data ?? []}
      />
    </section>
  );
}

function countByStation(rows: { station_id: number }[], stationId: number) {
  return rows.filter((row) => row.station_id === stationId).length;
}
