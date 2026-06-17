export type SeverityValue = "low" | "medium" | "high" | "critical";

type SeverityBadgeProps = {
  severity: SeverityValue;
};

const severityLabels: Record<SeverityValue, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical",
};

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  return <span className={`badge severity-${severity}`}>{severityLabels[severity]}</span>;
}
