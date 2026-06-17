import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatusBadge } from "../../components/ui/StatusBadge";

const rows = [
  { code: "torque_out_of_spec", station: "A-BODY", severity: "high" as const, status: "open" as const },
  { code: "vision_low_confidence", station: "A-PAINT", severity: "medium" as const, status: "investigating" as const },
];

export function DefectsPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Defects" description="Placeholder defect queue for future live workflow data." />
      <DataTable
        caption="Mock defects"
        columns={[
          { key: "code", header: "Defect Code", render: (row) => row.code },
          { key: "station", header: "Station", render: (row) => row.station },
          { key: "severity", header: "Severity", render: (row) => <SeverityBadge severity={row.severity} /> },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
        ]}
        rows={rows}
      />
    </section>
  );
}
