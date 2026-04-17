import { useCallback, useEffect, useState } from "react";
import { maloneApi } from "../../lib/maloneApi";

function JsonBlock({ label, value }) {
  const text =
    typeof value === "string" ? value : JSON.stringify(value ?? null, null, 2);
  const rows = Math.min(30, Math.max(6, 6 + Math.floor(text.length / 120)));
  return (
    <div className="stack" style={{ marginTop: "0.75rem" }}>
      {label ? <strong>{label}</strong> : null}
      <textarea
        readOnly
        className="info-text"
        rows={rows}
        value={text}
        style={{
          width: "100%",
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
          fontSize: "0.85rem",
        }}
      />
    </div>
  );
}

function MaybeCollapsedJson({ label, value, collapsed }) {
  const inner = <JsonBlock label="" value={value} />;
  if (!collapsed) {
    return <JsonBlock label={label} value={value} />;
  }
  return (
    <details style={{ marginTop: "0.75rem" }} className="info-text">
      <summary style={{ cursor: "pointer" }}>
        <strong>{label}</strong> — expand for raw JSON
      </summary>
      <div style={{ marginTop: "0.5rem" }}>{inner}</div>
    </details>
  );
}

export default function MaloneInspectionPanel({ response }) {
  const [open, setOpen] = useState(() => {
    try {
      return window.localStorage?.getItem("malone_inspect_open") === "1";
    } catch {
      return false;
    }
  });
  const [traceDetail, setTraceDetail] = useState(null);
  const [traceError, setTraceError] = useState("");
  const [traceLoading, setTraceLoading] = useState(false);

  useEffect(() => {
    try {
      window.localStorage?.setItem("malone_inspect_open", open ? "1" : "0");
    } catch {
      /* ignore */
    }
  }, [open]);

  const demoActive = Boolean(response?.demo?.active);
  const telemetry = response?.malone_telemetry ?? null;
  const sid =
    telemetry?.trace_ids?.scenario_memory_id ||
    response?.truth_packet?.scenario_memory_id ||
    response?.truth_packet?.packet_meta?.scenario_memory_id ||
    null;

  const loadTrace = useCallback(async () => {
    if (!sid) {
      setTraceError("No scenario_memory_id on this response.");
      return;
    }
    setTraceLoading(true);
    setTraceError("");
    try {
      const row = await maloneApi.getInspectTrace(sid);
      setTraceDetail(row);
    } catch (e) {
      setTraceDetail(null);
      setTraceError(e instanceof Error ? e.message : String(e));
    } finally {
      setTraceLoading(false);
    }
  }, [sid]);

  if (!open) {
    return (
      <div className="card" style={{ opacity: 0.92 }}>
        <button type="button" className="secondary-button" onClick={() => setOpen(true)}>
          Show read-only inspection (telemetry / traces)
        </button>
        <div className="info-text" style={{ marginTop: "0.5rem" }}>
          Debug-only view. Does not change Malone answers or stored traces.
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ borderStyle: "dashed" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>Read-only inspection</h3>
        <button type="button" className="secondary-button" onClick={() => setOpen(false)}>
          Hide
        </button>
      </div>
      <p className="info-text">
        Observational metadata for this Malone turn. Current evidence and citations remain authoritative; prior
        scenario memory is secondary only.
      </p>

      {telemetry ? (
        <MaybeCollapsedJson
          label="malone_telemetry (this response)"
          value={telemetry}
          collapsed={demoActive}
        />
      ) : (
        <div className="info-text">No malone_telemetry on the latest response yet.</div>
      )}

      {response?.truth_packet?.operating_copilot ? (
        <MaybeCollapsedJson
          label="truth_packet.operating_copilot (subset)"
          value={response.truth_packet.operating_copilot}
          collapsed={demoActive}
        />
      ) : null}

      {response?.truth_packet?.decision_workflow ? (
        <MaybeCollapsedJson
          label="truth_packet.decision_workflow (subset)"
          value={response.truth_packet.decision_workflow}
          collapsed={demoActive}
        />
      ) : null}

      <div style={{ marginTop: "0.75rem", display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
        <button
          type="button"
          className="secondary-button"
          onClick={() => void loadTrace()}
          disabled={traceLoading || !sid}
          title={sid ? `Fetch persisted trace ${sid}` : "No scenario_memory_id"}
        >
          {traceLoading ? "Loading trace…" : "Load persisted trace (read-only API)"}
        </button>
        {!sid ? <span className="info-text">No trace id on this turn (memory may be off or ineligible).</span> : null}
      </div>
      {traceError ? <div className="error-text">{traceError}</div> : null}
      {traceDetail ? (
        <MaybeCollapsedJson label="GET /api/malone/inspect/traces/{id}" value={traceDetail} collapsed={demoActive} />
      ) : null}
    </div>
  );
}
