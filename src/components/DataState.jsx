export default function DataState({ loading, error, empty, children }) {
  if (loading) return <div className="card">Loading…</div>
  if (error) return <div className="card error">Error: {String(error.message || error)}</div>
  if (empty) return <div className="card">No data yet.</div>
  return children
}
