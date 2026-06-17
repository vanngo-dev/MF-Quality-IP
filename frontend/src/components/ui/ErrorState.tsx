type ErrorStateProps = {
  message?: string;
};

export function ErrorState({ message = "Unable to load manufacturing quality data." }: ErrorStateProps) {
  return <div className="state-panel state-error">{message}</div>;
}
