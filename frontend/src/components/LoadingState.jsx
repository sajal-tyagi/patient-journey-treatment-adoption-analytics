export function LoadingState({ message = 'Loading analytics…' }) {
  return (
    <div className="state-center">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  );
}

export function ErrorState({ message }) {
  return (
    <div className="error-box" role="alert">
      <strong>⚠ Unable to load data</strong>
      <p style={{ marginTop: '6px' }}>
        {message || 'Make sure the backend is running: uvicorn api.index:app --reload --port 8000'}
      </p>
    </div>
  );
}
