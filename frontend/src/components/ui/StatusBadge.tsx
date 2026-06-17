export type StatusValue =
  | "open"
  | "acknowledged"
  | "investigating"
  | "contained"
  | "resolved"
  | "draft"
  | "active"
  | "waiting_on_data";

type StatusBadgeProps = {
  status: StatusValue;
};

const statusLabels: Record<StatusValue, string> = {
  open: "Open",
  acknowledged: "Acknowledged",
  investigating: "Investigating",
  contained: "Contained",
  resolved: "Resolved",
  draft: "Draft",
  active: "Active",
  waiting_on_data: "Waiting on Data",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`badge status-${status}`}>{statusLabels[status]}</span>;
}
