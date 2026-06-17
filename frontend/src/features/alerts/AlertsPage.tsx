import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatusBadge } from "../../components/ui/StatusBadge";

const rows = [
  { code: "REPEATED_DEFECT_STATION", station: "A-BODY", severity: "high" as const, status: "open" as const },
  { code: "VISION_CONFIDENCE_LOW", station: "A-PAINT", severity: "medium" as const, status: "acknowledged" as const },
];

export function AlertsPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Alerts" description="Placeholder alert queue for rule-based quality signals." />
      <DataTable
        caption="Mock alerts"
        columns={[
          { key: "code", header: "Alert Code", render: (row) => row.code },
          { key: "station", header: "Station", render: (row) => row.station },
          { key: "severity", header: "Severity", render: (row) => <SeverityBadge severity={row.severity} /> },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
        ]}
        rows={rows}
      />
    </section>
  );
}
