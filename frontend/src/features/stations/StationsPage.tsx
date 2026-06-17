import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";

const rows = [
  { code: "A-BODY", name: "Body Fit", line: "LINE-A", order: "10" },
  { code: "A-PAINT", name: "Paint Inspection", line: "LINE-A", order: "20" },
  { code: "A-FINAL", name: "Final Quality Gate", line: "LINE-A", order: "30" },
];

export function StationsPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Stations" description="Placeholder station list prepared for Phase 9 live API data." />
      <DataTable
        caption="Mock stations"
        columns={[
          { key: "code", header: "Code", render: (row) => row.code },
          { key: "name", header: "Name", render: (row) => row.name },
          { key: "line", header: "Line", render: (row) => row.line },
          { key: "order", header: "Sequence", render: (row) => row.order },
        ]}
        rows={rows}
      />
    </section>
  );
}
