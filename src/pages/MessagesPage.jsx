import { useEffect, useState } from "react";
import { api } from "../lib/api";

function formatMeta(meta) {
  if (!meta) return "-";
  if (typeof meta === "string") return meta;
  return JSON.stringify(meta, null, 2);
}

export default function MessagesPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        setLoading(true);
        setError("");
        const data = await api.getMessages();
        if (mounted) {
          setRows(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (mounted) {
          setError(err.message || "Failed to load messages");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1>Messages</h1>
          <p>Queued, processed, and logged message activity.</p>
        </div>
      </div>

      {loading ? <div className="card">Loading messages...</div> : null}
      {error ? <div className="card error error-text">Error: {error}</div> : null}

      {!loading && !error ? (
        <div className="card">
          {rows.length === 0 ? (
            <div className="empty-state">No message records found.</div>
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Action</th>
                    <th>Entity ID</th>
                    <th>Actor</th>
                    <th>Created</th>
                    <th>Meta</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={String(row.id)}>
                      <td>{String(row.id)}</td>
                      <td>{row.action ?? "-"}</td>
                      <td>{row.entity_id ?? "-"}</td>
                      <td>{row.actor_user_id ?? "-"}</td>
                      <td>{row.created_at ?? "-"}</td>
                      <td>
                        <pre className="inline-json">{formatMeta(row.meta_json)}</pre>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : null}
    </section>
  );
}