import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";

const rows = [
  { asset: "EQ-A-ROBOT-01", name: "Body Weld Robot A1", type: "robot", station: "A-BODY" },
  { asset: "EQ-A-TORQUE-02", name: "Door Torque Tool A2", type: "torque_tool", station: "A-BODY" },
  { asset: "EQ-A-VISION-03", name: "Paint Vision Camera A3", type: "vision_system", station: "A-PAINT" },
];

export function EquipmentPage() {
  return (
    <section className="page-stack">
      <PageHeader title="Equipment" description="Placeholder equipment inventory for the dashboard foundation." />
      <DataTable
        caption="Mock equipment"
        columns={[
          { key: "asset", header: "Asset Tag", render: (row) => row.asset },
          { key: "name", header: "Name", render: (row) => row.name },
          { key: "type", header: "Type", render: (row) => row.type },
          { key: "station", header: "Station", render: (row) => row.station },
        ]}
        rows={rows}
      />
    </section>
  );
}
