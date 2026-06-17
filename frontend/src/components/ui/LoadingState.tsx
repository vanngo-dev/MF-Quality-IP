type LoadingStateProps = {
  message?: string;
};

export function LoadingState({ message = "Loading manufacturing quality data..." }: LoadingStateProps) {
  return <div className="state-panel state-loading">{message}</div>;
}
