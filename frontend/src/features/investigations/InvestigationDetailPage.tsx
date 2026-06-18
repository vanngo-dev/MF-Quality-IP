import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { PageHeader } from "../../components/layout/PageHeader";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getAlertById, updateAlertStatus } from "../../services/alertsApi";
import {
  generateInvestigationAiSummary,
  getInvestigationById,
  updateInvestigation,
  updateInvestigationStatus,
} from "../../services/investigationsApi";
import { AlertStatusActions } from "../alerts/AlertStatusActions";
import { AiSummaryPanel } from "./components/AiSummaryPanel";
import { EvidencePanel } from "./components/EvidencePanel";
import { InvestigationForm, type InvestigationFormValues } from "./components/InvestigationForm";
import { InvestigationStatusActions } from "./components/InvestigationStatusActions";
import { TimelinePanel } from "./components/TimelinePanel";

export function InvestigationDetailPage() {
  const { investigationId } = useParams();
  const numericInvestigationId = Number(investigationId);
  const queryClient = useQueryClient();
  const investigationQuery = useQuery({
    queryKey: ["investigation", numericInvestigationId],
    queryFn: () => getInvestigationById(numericInvestigationId),
    enabled: Number.isFinite(numericInvestigationId),
  });
  const alertQuery = useQuery({
    queryKey: ["alert", investigationQuery.data?.alert_id],
    queryFn: () => getAlertById(investigationQuery.data?.alert_id ?? 0),
    enabled: Boolean(investigationQuery.data?.alert_id),
  });
  const updateMutation = useMutation({
    mutationFn: (values: InvestigationFormValues) =>
      updateInvestigation(numericInvestigationId, {
        title: values.title,
        summary: values.summary || null,
        root_cause_hypothesis: values.root_cause_hypothesis || null,
        status: values.status,
      }),
    onSuccess: (investigation) => {
      invalidateInvestigationQueries(queryClient, investigation.id, investigation.alert_id);
    },
  });
  const statusMutation = useMutation({
    mutationFn: (status: string) => updateInvestigationStatus(numericInvestigationId, status),
    onSuccess: (investigation) => {
      invalidateInvestigationQueries(queryClient, investigation.id, investigation.alert_id);
    },
  });
  const alertStatusMutation = useMutation({
    mutationFn: (status: string) => updateAlertStatus(investigationQuery.data?.alert_id ?? 0, status),
    onSuccess: (alert) => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
      void queryClient.invalidateQueries({ queryKey: ["alert", alert.id] });
    },
  });
  const aiSummaryMutation = useMutation({
    mutationFn: () => generateInvestigationAiSummary(numericInvestigationId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["investigation", numericInvestigationId] });
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
  });

  if (investigationQuery.isLoading || (investigationQuery.data && alertQuery.isLoading)) {
    return <LoadingState message="Loading investigation detail..." />;
  }

  if (investigationQuery.isError || alertQuery.isError) {
    return <ErrorState message="Unable to load investigation detail from the backend API." />;
  }

  const investigation = investigationQuery.data;
  const alert = alertQuery.data;

  if (!investigation) {
    return <ErrorState message="Investigation not found." />;
  }

  return (
    <section className="page-stack" data-testid="investigation-detail-page">
      <PageHeader title={investigation.title} description="Update engineering notes, status, and linked alert resolution." />

      <section className="detail-panel">
        <div className="detail-heading">
          <div>
            <p className="eyebrow">Investigation {investigation.id}</p>
            <h2>{investigation.title}</h2>
          </div>
          <StatusBadge status={investigation.status} />
        </div>
        <dl className="detail-grid">
          <div>
            <dt>Linked Alert</dt>
            <dd>
              <Link className="text-link" to={`/alerts/${investigation.alert_id}`}>
                Alert {investigation.alert_id}
              </Link>
            </dd>
          </div>
          <div>
            <dt>Created</dt>
            <dd>{formatDate(investigation.created_at ?? investigation.opened_at)}</dd>
          </div>
          <div>
            <dt>Updated</dt>
            <dd>{formatDate(investigation.updated_at)}</dd>
          </div>
          <div>
            <dt>AI Summary</dt>
            <dd>{investigation.ai_summary ? "Generated" : "Not generated yet"}</dd>
          </div>
        </dl>
      </section>

      <AiSummaryPanel
        isError={aiSummaryMutation.isError}
        isGenerating={aiSummaryMutation.isPending}
        onGenerate={() => aiSummaryMutation.mutate()}
        summary={aiSummaryMutation.data?.ai_summary ?? investigation.ai_summary}
      />

      <div className="workflow-grid">
        <EvidencePanel evidence={investigation.evidence_json} title="Investigation Evidence" />
        <TimelinePanel
          items={[
            { label: "Alert created", timestamp: alert?.created_at },
            { label: "Investigation created", timestamp: investigation.created_at ?? investigation.opened_at },
            { label: "Investigation updated", timestamp: investigation.updated_at },
            {
              label: "Investigation resolved",
              timestamp: investigation.status === "resolved" ? investigation.closed_at : null,
            },
          ]}
        />
      </div>

      <section className="workflow-panel" aria-label="Investigation edit form">
        <h2>Edit Investigation</h2>
        <InvestigationForm
          initialValues={{
            title: investigation.title,
            summary: investigation.summary ?? "",
            root_cause_hypothesis: investigation.root_cause_hypothesis ?? "",
            status: investigation.status,
          }}
          isSaving={updateMutation.isPending}
          onSubmit={(values) => updateMutation.mutate(values)}
          submitLabel="Save Changes"
        />
      </section>

      <InvestigationStatusActions
        isSaving={statusMutation.isPending}
        onStatusChange={(status) => statusMutation.mutate(status)}
        status={investigation.status}
      />

      {alert ? (
        <AlertStatusActions
          isSaving={alertStatusMutation.isPending}
          onStatusChange={(status) => alertStatusMutation.mutate(status)}
          status={alert.status}
        />
      ) : null}
    </section>
  );
}

function invalidateInvestigationQueries(
  queryClient: ReturnType<typeof useQueryClient>,
  investigationId: number,
  alertId: number,
) {
  void queryClient.invalidateQueries({ queryKey: ["investigations"] });
  void queryClient.invalidateQueries({ queryKey: ["investigation", investigationId] });
  void queryClient.invalidateQueries({ queryKey: ["alerts"] });
  void queryClient.invalidateQueries({ queryKey: ["alert", alertId] });
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
