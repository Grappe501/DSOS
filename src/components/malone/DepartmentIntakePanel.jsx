import { useCallback, useState } from "react";
import { maloneApi } from "../../lib/maloneApi";

/**
 * Minimal department intake surface: start session, post answers, materialize map, view map.
 * Uses the same authenticated Malone API path as chat (no separate bot).
 */
const DEMO_INTAKE_PRESETS = [
  { label: "Pharmacy — intake desk", name: "Pharmacy Intake" },
  { label: "Prior authorization", name: "Prior Authorization" },
];

export default function DepartmentIntakePanel({ demoActive = false }) {
  const [departmentName, setDepartmentName] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [answerText, setAnswerText] = useState("");
  const [questionKey, setQuestionKey] = useState("mission");
  const [entryMode, setEntryMode] = useState("text");
  const [detail, setDetail] = useState(null);
  const [mapView, setMapView] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async (sid) => {
    if (!sid) return;
    const d = await maloneApi.operationsMapGetIntakeSession(sid);
    setDetail(d);
  }, []);

  const onStart = useCallback(async () => {
    setError(null);
    setBusy(true);
    try {
      const out = await maloneApi.operationsMapStartIntake({
        department_name: departmentName.trim() || "Unnamed department",
      });
      setSessionId(out.intake_session_id);
      setDepartmentId(out.operations_department_id);
      await refresh(out.intake_session_id);
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  }, [departmentName, refresh]);

  const onAnswer = useCallback(async () => {
    if (!sessionId || !answerText.trim()) return;
    setError(null);
    setBusy(true);
    try {
      await maloneApi.operationsMapPostAnswer(sessionId, {
        text: answerText,
        question_key: questionKey || null,
        entry_mode: entryMode,
      });
      setAnswerText("");
      await refresh(sessionId);
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  }, [sessionId, answerText, questionKey, entryMode, refresh]);

  const onMaterialize = useCallback(async () => {
    if (!sessionId) return;
    setError(null);
    setBusy(true);
    try {
      await maloneApi.operationsMapMaterialize(sessionId);
      const m = await maloneApi.operationsMapGetDepartmentMap(departmentId);
      setMapView(m);
    } catch (e) {
      setError(String(e?.message || e));
    } finally {
      setBusy(false);
    }
  }, [sessionId, departmentId]);

  return (
    <section className="malone-intake-panel" style={{ marginTop: "1rem", padding: "0.75rem", border: "1px solid #3336", borderRadius: 8 }}>
      <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem" }}>Department intake (operations map)</h3>
      <p style={{ margin: "0 0 0.5rem", fontSize: "0.85rem", opacity: 0.85 }}>
        Draft only — does not replace policy/legal evidence. Same login as Malone chat.
      </p>
      {demoActive ? (
        <div style={{ marginBottom: 8, display: "flex", flexWrap: "wrap", gap: 6 }}>
          {DEMO_INTAKE_PRESETS.map((p) => (
            <button
              key={p.name}
              type="button"
              className="secondary-button"
              style={{ fontSize: "0.8rem" }}
              onClick={() => setDepartmentName(p.name)}
            >
              {p.label}
            </button>
          ))}
        </div>
      ) : null}
      {error ? (
        <p style={{ color: "coral", fontSize: "0.85rem" }} role="alert">
          {error}
        </p>
      ) : null}
      <label style={{ display: "block", marginBottom: 6 }}>
        Department name
        <input
          style={{ display: "block", width: "100%", marginTop: 4 }}
          value={departmentName}
          onChange={(e) => setDepartmentName(e.target.value)}
          placeholder="e.g. Pharmacy Operations"
        />
      </label>
      <button type="button" disabled={busy} onClick={onStart}>
        Start intake session
      </button>
      {sessionId ? (
        <p style={{ fontSize: "0.8rem", marginTop: 8 }}>
          Session: <code>{sessionId}</code>
        </p>
      ) : null}
      {detail?.followup_questions?.length ? (
        <ul style={{ fontSize: "0.8rem", margin: "0.5rem 0" }}>
          {detail.followup_questions.slice(0, 5).map((q) => (
            <li key={q.target_field}>
              <strong>{q.target_field}</strong>: {q.question_text}
            </li>
          ))}
        </ul>
      ) : null}
      {sessionId ? (
        <>
          <label style={{ display: "block", marginTop: 8 }}>
            Question key (optional)
            <input style={{ display: "block", width: "100%" }} value={questionKey} onChange={(e) => setQuestionKey(e.target.value)} />
          </label>
          <label style={{ display: "block", marginTop: 8 }}>
            Answer
            <textarea
              style={{ display: "block", width: "100%", minHeight: 64 }}
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
            />
          </label>
          <label style={{ display: "block", marginTop: 4, fontSize: "0.85rem" }}>
            Entry mode{" "}
            <select value={entryMode} onChange={(e) => setEntryMode(e.target.value)}>
              <option value="text">text</option>
              <option value="voice_transcript">voice_transcript</option>
            </select>
          </label>
          <button type="button" disabled={busy} onClick={onAnswer} style={{ marginTop: 6 }}>
            Record answer
          </button>
          <button type="button" disabled={busy} onClick={onMaterialize} style={{ marginLeft: 8 }}>
            Build operations map
          </button>
        </>
      ) : null}
      {mapView ? (
        <pre style={{ fontSize: "0.75rem", marginTop: 8, maxHeight: 240, overflow: "auto", background: "#1113", padding: 8 }}>
          {JSON.stringify(mapView, null, 2)}
        </pre>
      ) : null}
    </section>
  );
}
