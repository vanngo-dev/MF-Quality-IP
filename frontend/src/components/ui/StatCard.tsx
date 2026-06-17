type StatCardProps = {
  title: string;
  value: string;
  description?: string;
};

export function StatCard({ title, value, description }: StatCardProps) {
  return (
    <article className="stat-card">
      <span>{title}</span>
      <strong>{value}</strong>
      {description ? <p>{description}</p> : null}
    </article>
  );
}
