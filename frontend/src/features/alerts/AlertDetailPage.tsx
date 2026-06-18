import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { PageHeader } from "../../components/layout/PageHeader";
import { ErrorState } from "../../components/ui/ErrorState";
import { LoadingState } from "../../components/ui/LoadingState";
import { SeverityBadge } from "../../components/ui/SeverityBadge";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { getAlertById, updateAlertStatus } from "../../services/alertsApi";
import { getEquipment } from "../../services/equipmentApi";
import {
  createInvestigationFromAlert,
  getInvestigations,
  type Investigation,
} from "../../services/investigationsApi";
import { getStations } from "../../services/stationsApi";
import { AlertStatusActions } from "./AlertStatusActions";
import { EvidencePanel } from "../investigations/components/EvidencePanel";
import { InvestigationForm, type InvestigationFormValues } from "../investigations/components/InvestigationForm";
import { TimelinePanel } from "../investigations/components/TimelinePanel";

export function AlertDetailPage() {
  const { alertId } = useParams();
  const numericAlertId = Number(alertId);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const alertQuery = useQuery({
    queryKey: ["alert", numericAlertId],
    queryFn: () => getAlertById(numericAlertId),
    enabled: Number.isFinite(numericAlertId),
  });
  const investigationsQuery = useQuery({ queryKey: ["investigations"], queryFn: getInvestigations });
  const stationsQuery = useQuery({ queryKey: ["stations"], queryFn: getStations });
  const equipmentQuery = useQuery({ queryKey: ["equipment"], queryFn: getEquipment });
  const statusMutation = useMutation({
    mutationFn: (status: string) => updateAlertStatus(numericAlertId, status),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
      void queryClient.invalidateQueries({ queryKey: ["alert", numericAlertId] });
    },
  });
  const createInvestigationMutation = useMutation({
    mutationFn: (values: InvestigationFormValues) =>
      createInvestigationFromAlert(numericAlertId, {
        title: values.title,
        summary: values.summary || null,
        root_cause_hypothesis: values.root_cause_hypothesis || null,
        status: values.status,
      }),
    onSuccess: (investigation) => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
      void queryClient.invalidateQueries({ queryKey: ["alert", numericAlertId] });
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
      navigate(`/investigations/${investigation.id}`);
    },
  });
  const existingInvestigation = useMemo(() => {
    return (investigationsQuery.data ?? []).find(
      (investigation) => investigation.alert_id === numericAlertId && investigation.status !== "resolved",
    );
  }, [investigationsQuery.data, numericAlertId]);

  if (alertQuery.isLoading || investigationsQuery.isLoading || stationsQuery.isLoading || equipmentQuery.isLoading) {
    return <LoadingState message="Loading alert detail..." />;
  }

  if (alertQuery.isError || investigationsQuery.isError || stationsQuery.isError || equipmentQuery.isError) {
    return <ErrorState message="Unable to load alert detail from the backend API." />;
  }

  const alert = alertQuery.data;

  if (!alert) {
    return <ErrorState message="Alert not found." />;
  }

  const stations = stationsQuery.data ?? [];
  const equipment = equipmentQuery.data ?? [];

  return (
    <section className="page-stack" data-testid="alert-detail-page">
      <PageHeader title={alert.title} description="Review alert evidence and open an engineering investigation." />

      <section className="detail-panel">
        <div className="detail-heading">
          <div>
            <p className="eyebrow">{alert.alert_code}</p>
            <h2>{alert.title}</h2>
          </div>
          <div className="table-actions">
            <SeverityBadge severity={alert.severity} />
            <StatusBadge status={alert.status} />
          </div>
        </div>
        <dl className="detail-grid">
          <div>
            <dt>Station</dt>
            <dd>{stationLabel(alert.station_id, stations)}</dd>
          </div>
          <div>
            <dt>Equipment</dt>
            <dd>{equipmentLabel(alert.equipment_id, equipment)}</dd>
          </div>
          <div>
            <dt>Created</dt>
            <dd>{formatDate(alert.created_at)}</dd>
          </div>
          <div>
            <dt>Alert ID</dt>
            <dd>{alert.id}</dd>
          </div>
        </dl>
        <p className="detail-copy">{alert.description}</p>
      </section>

      <div className="workflow-grid">
        <EvidencePanel evidence={alert.evidence_json} title="Alert Evidence" />
        <TimelinePanel items={[{ label: "Alert created", timestamp: alert.created_at }]} />
      </div>

      <AlertStatusActions
        isSaving={statusMutation.isPending}
        onStatusChange={(status) => statusMutation.mutate(status)}
        status={alert.status}
      />

      {existingInvestigation ? (
        <ExistingInvestigationPanel investigation={existingInvestigation} />
      ) : (
        <section className="workflow-panel" aria-label="Create investigation">
          <div className="workflow-panel-header">
            <h2>Create Investigation</h2>
            <button
              className="secondary-button compact"
              data-testid="create-investigation-button"
              type="button"
              onClick={() => setIsFormOpen((value) => !value)}
            >
              {isFormOpen ? "Close Form" : "Create Investigation"}
            </button>
          </div>
          {isFormOpen ? (
            <InvestigationForm
              initialValues={{
                title: `Investigate ${alert.title}`,
                summary: "Initial investigation opened from quality alert.",
                root_cause_hypothesis: "",
                status: "active",
              }}
              isSaving={createInvestigationMutation.isPending}
              onSubmit={(values) => createInvestigationMutation.mutate(values)}
              submitLabel="Save Investigation"
            />
          ) : null}
          {createInvestigationMutation.isError ? (
            <ErrorState message="Unable to create investigation for this alert." />
          ) : null}
        </section>
      )}
    </section>
  );
}

function ExistingInvestigationPanel({ investigation }: { investigation: Investigation }) {
  return (
    <section className="workflow-panel" aria-label="Existing investigation">
      <h2>Existing Investigation</h2>
      <p>{investigation.title}</p>
      <Link className="text-link" to={`/investigations/${investigation.id}`}>
        Open Investigation
      </Link>
    </section>
  );
}

function stationLabel(stationId: number, stations: { id: number; code: string }[]) {
  return stations.find((station) => station.id === stationId)?.code ?? `Station ${stationId}`;
}

function equipmentLabel(equipmentId: number | null, equipment: { id: number; asset_tag: string }[]) {
  if (equipmentId === null) {
    return "Not specified";
  }

  return equipment.find((item) => item.id === equipmentId)?.asset_tag ?? `Equipment ${equipmentId}`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
