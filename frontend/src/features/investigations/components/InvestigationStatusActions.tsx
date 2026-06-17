type InvestigationStatusActionsProps = {
  isSaving?: boolean;
  onStatusChange: (status: string) => void;
  status: string;
};

const statuses = [
  { label: "Mark Active", value: "active" },
  { label: "Waiting on Data", value: "waiting_on_data" },
  { label: "Resolve Investigation", value: "resolved" },
];

export function InvestigationStatusActions({
  isSaving = false,
  onStatusChange,
  status,
}: InvestigationStatusActionsProps) {
  return (
    <section className="workflow-panel" aria-label="Investigation status actions">
      <h2>Status Actions</h2>
      <div className="table-actions">
        {statuses.map((item) => (
          <button
            className="secondary-button compact"
            disabled={isSaving || status === item.value}
            key={item.value}
            onClick={() => onStatusChange(item.value)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </div>
    </section>
  );
}
