import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getEquipment } from "../../services/equipmentApi";
import { getStations } from "../../services/stationsApi";

export function EquipmentPage() {
  const equipmentQuery = useQuery({ queryKey: ["equipment"], queryFn: getEquipment });
  const stationsQuery = useQuery({ queryKey: ["stations"], queryFn: getStations });

  if (equipmentQuery.isLoading || stationsQuery.isLoading) {
    return <LoadingState message="Loading equipment..." />;
  }

  if (equipmentQuery.isError || stationsQuery.isError) {
    return <ErrorState message="Unable to load equipment data from the backend API." />;
  }

  const stations = stationsQuery.data ?? [];

  return (
    <section className="page-stack">
      <PageHeader title="Equipment" description="Live equipment inventory from the backend API." />
      <DataTable
        caption="Equipment"
        columns={[
          { key: "asset", header: "Equipment Code", render: (row) => row.asset_tag },
          { key: "name", header: "Name", render: (row) => row.name },
          { key: "type", header: "Type", render: (row) => row.equipment_type },
          { key: "station", header: "Station", render: (row) => stationLabel(row.station_id, stations) },
          { key: "status", header: "Status", render: () => <StatusBadge status="active" /> },
        ]}
        rows={equipmentQuery.data ?? []}
      />
    </section>
  );
}

function stationLabel(stationId: number, stations: { id: number; code: string }[]) {
  return stations.find((station) => station.id === stationId)?.code ?? `Station ${stationId}`;
}
