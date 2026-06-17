export type SeverityValue = "low" | "medium" | "high" | "critical";

type SeverityBadgeProps = {
  severity: SeverityValue | string;
};

const severityLabels: Record<SeverityValue, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical",
};

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const label = severity in severityLabels ? severityLabels[severity as SeverityValue] : severity;

  return <span className={`badge severity-${severity}`}>{label}</span>;
}
