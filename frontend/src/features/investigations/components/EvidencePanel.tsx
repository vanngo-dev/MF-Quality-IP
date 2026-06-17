type EvidencePanelProps = {
  evidence: Record<string, unknown> | null | undefined;
  title?: string;
};

export function EvidencePanel({ evidence, title = "Evidence" }: EvidencePanelProps) {
  const normalizedEvidence = evidence ?? {};

  return (
    <section className="workflow-panel" aria-label={title}>
      <h2>{title}</h2>
      <pre className="evidence-json">{JSON.stringify(normalizedEvidence, null, 2)}</pre>
    </section>
  );
}
