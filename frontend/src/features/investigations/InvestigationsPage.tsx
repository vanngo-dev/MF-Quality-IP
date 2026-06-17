import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { PageHeader } from "../../components/layout/PageHeader";
import { DataTable } from "../../components/ui/DataTable";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getInvestigations } from "../../services/investigationsApi";

export function InvestigationsPage() {
  const investigationsQuery = useQuery({ queryKey: ["investigations"], queryFn: getInvestigations });

  if (investigationsQuery.isLoading) {
    return <LoadingState message="Loading investigations..." />;
  }

  if (investigationsQuery.isError) {
    return <ErrorState message="Unable to load investigation data from the backend API." />;
  }

  return (
    <section className="page-stack">
      <PageHeader title="Investigations" description="Live investigation worklist for root-cause follow-up." />
      <DataTable
        caption="Investigations"
        columns={[
          {
            key: "title",
            header: "Title",
            render: (row) => (
              <Link className="text-link" to={`/investigations/${row.id}`}>
                {row.title}
              </Link>
            ),
          },
          { key: "alert", header: "Alert ID", render: (row) => row.alert_id },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
          {
            key: "hypothesis",
            header: "Root Cause Hypothesis",
            render: (row) => row.root_cause_hypothesis ?? "Not documented yet",
          },
          { key: "created", header: "Created", render: (row) => formatDate(row.opened_at) },
          { key: "updated", header: "Updated", render: (row) => formatDate(row.updated_at) },
        ]}
        rows={investigationsQuery.data ?? []}
      />
    </section>
  );
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
