type AlertStatusActionsProps = {
  isSaving?: boolean;
  onStatusChange: (status: string) => void;
  status: string;
};

const statuses = [
  { label: "Acknowledge Alert", value: "acknowledged" },
  { label: "Mark Investigating", value: "investigating" },
  { label: "Resolve Alert", value: "resolved" },
];

export function AlertStatusActions({ isSaving = false, onStatusChange, status }: AlertStatusActionsProps) {
  return (
    <section className="workflow-panel" aria-label="Alert status actions">
      <h2>Alert Actions</h2>
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
