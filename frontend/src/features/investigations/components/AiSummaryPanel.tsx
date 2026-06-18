import type { AiSummaryContent } from "../../../services/investigationsApi";

type AiSummaryPanelProps = {
  isGenerating?: boolean;
  isError?: boolean;
  onGenerate: () => void;
  summary: AiSummaryContent | null;
};

export function AiSummaryPanel({ isError = false, isGenerating = false, onGenerate, summary }: AiSummaryPanelProps) {
  return (
    <section className="workflow-panel" aria-label="AI Summary">
      <div className="workflow-panel-header">
        <h2>AI Summary</h2>
        <button className="secondary-button compact" disabled={isGenerating} onClick={onGenerate} type="button">
          {summary ? "Regenerate AI Summary" : "Generate AI Summary"}
        </button>
      </div>

      {isGenerating ? <p className="state-panel state-loading">Generating AI summary...</p> : null}
      {isError ? <p className="state-panel state-error">Unable to generate AI summary.</p> : null}

      {summary ? (
        <div className="ai-summary-content">
          <div className="ai-summary-main">
            <span className={`confidence-badge confidence-${summary.confidence}`}>{summary.confidence}</span>
            <div>
              <h3>Likely Issue</h3>
              <p>{summary.likely_issue}</p>
            </div>
          </div>
          <dl className="detail-grid compact-grid">
            <div>
              <dt>Affected Station</dt>
              <dd>{summary.affected_station ?? "Not identified"}</dd>
            </div>
            <div>
              <dt>Affected Equipment</dt>
              <dd>{summary.affected_equipment ?? "Not identified"}</dd>
            </div>
          </dl>
          <ListSection title="Evidence" items={summary.evidence} />
          <ListSection title="Recommended Next Checks" items={summary.recommended_next_checks} />
          <ListSection title="Limitations" items={summary.limitations} />
        </div>
      ) : (
        <p>Generate a grounded summary from linked alerts, defects, sensor readings, station events, and investigation notes.</p>
      )}
    </section>
  );
}

function ListSection({ items, title }: { items: string[]; title: string }) {
  return (
    <div className="ai-summary-list">
      <h3>{title}</h3>
      {items.length > 0 ? (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>Not available.</p>
      )}
    </div>
  );
}
