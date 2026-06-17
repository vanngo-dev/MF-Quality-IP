import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { StatusBadge } from "../../components/ui/StatusBadge";

const rows = [
  { vin: "MQPLANT0000000001", model: "Aster EV", station: "A-BODY", status: "active" as const },
  { vin: "MQPLANT0000000002", model: "Aster EV", station: "A-PAINT", status: "active" as const },
  { vin: "MQPLANT0000000010", model: "Summit EV", station: "B-FINAL", status: "contained" as const },
];

export function VehiclesPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Vehicles" description="Placeholder vehicle work-in-process view for Phase 8." />
      <DataTable
        caption="Mock vehicles"
        columns={[
          { key: "vin", header: "VIN", render: (row) => row.vin },
          { key: "model", header: "Model", render: (row) => row.model },
          { key: "station", header: "Current Station", render: (row) => row.station },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
        ]}
        rows={rows}
      />
    </section>
  );
}
