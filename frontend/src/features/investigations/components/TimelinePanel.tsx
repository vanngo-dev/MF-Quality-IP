export type TimelineItem = {
  label: string;
  timestamp: string | null | undefined;
};

type TimelinePanelProps = {
  items: TimelineItem[];
};

export function TimelinePanel({ items }: TimelinePanelProps) {
  const visibleItems = items.filter((item) => item.timestamp);

  return (
    <section className="workflow-panel" aria-label="Timeline">
      <h2>Timeline</h2>
      <ol className="timeline-list">
        {visibleItems.map((item) => (
          <li key={`${item.label}-${item.timestamp}`}>
            <span>{item.label}</span>
            <time dateTime={item.timestamp ?? undefined}>{formatDate(item.timestamp)}</time>
          </li>
        ))}
      </ol>
    </section>
  );
}

function formatDate(value: string | null | undefined) {
  return value ? new Date(value).toLocaleString() : "Not available";
}
