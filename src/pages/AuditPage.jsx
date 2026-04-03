import { useEffect, useState } from "react";

export default function AuditPage() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    setRows([]);
  }, []);

  return (
    <section>
      <h1>Audit</h1>
      <p>Actor-aware writes, request IDs, before/after snapshots, and admin review tooling</p>
      <div className="card">
        <strong>Starter scaffold</strong>
        <p>Wire audit filters, query state, and review table here.</p>
        <pre>{JSON.stringify(rows, null, 2)}</pre>
      </div>
    </section>
  );
}
