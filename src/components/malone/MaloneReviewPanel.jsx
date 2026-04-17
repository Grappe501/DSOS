import { useCallback, useEffect, useState } from "react";
import { maloneApi } from "../../lib/maloneApi";

const OUTCOMES = ["approved", "rejected", "needs_revision", "informational", "risk_flag"];

export default function MaloneReviewPanel({ response }) {
  const [open, setOpen] = useState(false);
  const [role, setRole] = useState("");
  const [artifactType, setArtifactType] = useState("normalized_unit");
  const [artifactId, setArtifactId] = useState("");
  const [outcome, setOutcome] = useState("approved");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const me = await maloneApi.me();
        if (!cancelled && me?.role) {
          setRole(me.role);
        }
      } catch {
        if (!cancelled) {
          setRole("");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const tid =
      response?.malone_governance?.normalized_units?.[0]?.normalized_unit_id ||
      response?.truth_packet?.scenario_memory_id ||
      "";
    if (tid && !artifactId) {
      setArtifactId(tid);
    }
  }, [response, artifactId]);

  const canReview = role === "owner" || role === "admin";

  const onSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setMsg("");
      const aid = artifactId.trim();
      if (!aid) {
        setMsg("Enter an artifact id.");
        return;
      }
      setBusy(true);
      try {
        await maloneApi.reviewSubmitFeedback({
          artifact_type: artifactType,
          artifact_id: aid,
          outcome,
          notes: notes.trim() || null,
        });
        setMsg("Review recorded (auditable). Source evidence is unchanged.");
        setNotes("");
      } catch (err) {
        setMsg(err instanceof Error ? err.message : String(err));
      } finally {
        setBusy(false);
      }
    },
    [artifactType, artifactId, notes, outcome],
  );

  if (!canReview) {
    return null;
  }

  if (!open) {
    return (
      <div className="card" style={{ opacity: 0.92 }}>
        <button type="button" className="secondary-button" onClick={() => setOpen(true)}>
          Human review (owner/admin)
        </button>
        <div className="info-text" style={{ marginTop: "0.5rem" }}>
          Governance only — does not rewrite sources or override citations.
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ borderStyle: "dashed" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>Human review</h3>
        <button type="button" className="secondary-button" onClick={() => setOpen(false)}>
          Hide
        </button>
      </div>
      <p className="info-text">
        Records an auditable review event and updates trust/review state where applicable. Current evidence remains
        primary.
      </p>
      <form className="form-card" onSubmit={onSubmit}>
        <label htmlFor="artifact-type">Artifact type</label>
        <select
          id="artifact-type"
          value={artifactType}
          onChange={(e) => setArtifactType(e.target.value)}
          disabled={busy}
        >
          <option value="normalized_unit">normalized_unit</option>
          <option value="scenario_memory">scenario_memory</option>
          <option value="decision_trace">decision_trace</option>
          <option value="operating_copilot_snapshot">operating_copilot_snapshot</option>
          <option value="website_pack_entry">website_pack_entry</option>
          <option value="ingestion_source_version">ingestion_source_version</option>
        </select>
        <label htmlFor="artifact-id">Artifact id</label>
        <input
          id="artifact-id"
          value={artifactId}
          onChange={(e) => setArtifactId(e.target.value)}
          disabled={busy}
          placeholder="e.g. normalized unit id or scenario_memory id"
        />
        <label htmlFor="outcome">Outcome</label>
        <select id="outcome" value={outcome} onChange={(e) => setOutcome(e.target.value)} disabled={busy}>
          {OUTCOMES.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
        <label htmlFor="notes">Notes (optional)</label>
        <textarea id="notes" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} disabled={busy} />
        <button className="primary-button" type="submit" disabled={busy}>
          {busy ? "Saving…" : "Submit review"}
        </button>
      </form>
      {msg ? <div className={msg.includes("recorded") ? "info-text" : "error-text"}>{msg}</div> : null}
    </div>
  );
}
