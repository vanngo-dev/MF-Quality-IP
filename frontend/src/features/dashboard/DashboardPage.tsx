import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatCard } from "../../components/ui/StatCard";
import { StatusBadge } from "../../components/ui/StatusBadge";

const stats = [
  { title: "Total Vehicles", value: "10", description: "Seeded vehicles tracked across active lines" },
  { title: "Open Defects", value: "3", description: "Mock queue for Phase 8 frontend shell" },
  { title: "Open Alerts", value: "2", description: "Rule-based alerts prepared for Phase 9 data" },
  { title: "Critical Alerts", value: "1", description: "Highest severity items needing review" },
];

const alertRows = [
  {
    code: "REPEATED_DEFECT_STATION",
    station: "A-BODY",
    severity: "high" as const,
    status: "open" as const,
  },
  {
    code: "TORQUE_OUT_OF_TOLERANCE",
    station: "A-BODY",
    severity: "critical" as const,
    status: "acknowledged" as const,
  },
];

export function DashboardPage() {
  return (
    <section className="page-stack">
      <PageHeader
        title="Dashboard"
        description="Operational summary shell for manufacturing quality signals. Phase 8 uses mock data only."
      />

      <div className="stat-grid">
        {stats.map((stat) => (
          <StatCard key={stat.title} title={stat.title} value={stat.value} description={stat.description} />
        ))}
      </div>

      <DataTable
        caption="Mock alert queue"
        columns={[
          { key: "code", header: "Alert Code", render: (row) => row.code },
          { key: "station", header: "Station", render: (row) => row.station },
          { key: "severity", header: "Severity", render: (row) => <SeverityBadge severity={row.severity} /> },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
        ]}
        rows={alertRows}
      />
    </section>
  );
}
