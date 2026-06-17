import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getAlerts, updateAlertStatus } from "../../services/alertsApi";
import { getEquipment } from "../../services/equipmentApi";
import { getStations } from "../../services/stationsApi";

export function AlertsPage() {
  const [severityFilter, setSeverityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const queryClient = useQueryClient();
  const alertsQuery = useQuery({ queryKey: ["alerts"], queryFn: getAlerts });
  const stationsQuery = useQuery({ queryKey: ["stations"], queryFn: getStations });
  const equipmentQuery = useQuery({ queryKey: ["equipment"], queryFn: getEquipment });
  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: number) => updateAlertStatus(alertId, "acknowledged"),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
  const filteredAlerts = useMemo(() => {
    return (alertsQuery.data ?? []).filter((alert) => {
      const matchesSeverity = severityFilter === "all" || alert.severity === severityFilter;
      const matchesStatus = statusFilter === "all" || alert.status === statusFilter;

      return matchesSeverity && matchesStatus;
    });
  }, [alertsQuery.data, severityFilter, statusFilter]);

  if (alertsQuery.isLoading || stationsQuery.isLoading || equipmentQuery.isLoading) {
    return <LoadingState message="Loading alerts..." />;
  }

  if (alertsQuery.isError || stationsQuery.isError || equipmentQuery.isError) {
    return <ErrorState message="Unable to load alert data from the backend API." />;
  }

  const stations = stationsQuery.data ?? [];
  const equipment = equipmentQuery.data ?? [];

  return (
    <section className="page-stack">
      <PageHeader title="Alerts" description="Live alert queue with filters and acknowledgement actions." />
      <div className="filter-row">
        <label>
          Severity
          <select value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)}>
            <option value="all">All severities</option>
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
            <option value="acknowledged">Acknowledged</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
          </select>
        </label>
      </div>
      <DataTable
        caption="Alerts"
        columns={[
          { key: "code", header: "Alert Code", render: (row) => row.alert_code },
          { key: "title", header: "Title", render: (row) => row.title },
          { key: "station", header: "Station", render: (row) => stationLabel(row.station_id, stations) },
          { key: "equipment", header: "Equipment", render: (row) => equipmentLabel(row.equipment_id, equipment) },
          { key: "severity", header: "Severity", render: (row) => <SeverityBadge severity={row.severity} /> },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
          { key: "created", header: "Created", render: (row) => formatDate(row.created_at) },
          { key: "description", header: "Description", render: (row) => row.description },
          {
            key: "actions",
            header: "Actions",
            render: (row) => (
              <div className="table-actions">
                {row.status === "open" ? (
                  <button
                    className="secondary-button compact"
                    type="button"
                    disabled={acknowledgeMutation.isPending}
                    onClick={() => acknowledgeMutation.mutate(row.id)}
                  >
                    Acknowledge
                  </button>
                ) : null}
                <Link className="text-link" to="/investigations">
                  Open Investigation
                </Link>
              </div>
            ),
          },
        ]}
        rows={filteredAlerts}
      />
    </section>
  );
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
