import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { StatusBadge } from "../../components/ui/StatusBadge";

const rows = [
  { title: "Investigate repeated torque defects", owner: "Quality Engineering", status: "draft" as const },
  { title: "Review low paint vision confidence", owner: "Process Engineering", status: "waiting_on_data" as const },
];

export function InvestigationsPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Investigations" description="Placeholder investigation worklist for root-cause follow-up." />
      <DataTable
        caption="Mock investigations"
        columns={[
          { key: "title", header: "Title", render: (row) => row.title },
          { key: "owner", header: "Owner", render: (row) => row.owner },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
        ]}
        rows={rows}
      />
    </section>
  );
}
