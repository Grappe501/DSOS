function renderJson(value) {
  return JSON.stringify(value ?? {}, null, 2);
}

export default function AgentRunPanel({ response }) {
  return (
    <div className="card">
      <h3>Execution Result</h3>
      {!response ? (
        <p>Malone execution results will appear here after validation and safe execution.</p>
      ) : response.result ? (
        <pre className="inline-json">{renderJson(response.result)}</pre>
      ) : (
        <div className="info-text">No executable result returned for this request.</div>
      )}
    </div>
  );
}