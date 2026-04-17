import MaloneAnswerPlayback from "./MaloneAnswerPlayback";

function renderJson(value) {
  return JSON.stringify(value ?? {}, null, 2);
}

function renderRecentProposal(row) {
  const label = [row.proposal_type, row.requested_action, row.target]
    .filter(Boolean)
    .join(" / ");

  return (
    <div key={row.id} className="info-text">
      <div>
        <strong>{label || row.id}</strong>
      </div>
      <div>Status: {row.execution_status} · Delivery: {row.delivery_status} · Validation: {row.validation_status}</div>
      <div>Actor: {row.actor_email || "-"}</div>
    </div>
  );
}

function DeliverySources({ sources = [] }) {
  if (!Array.isArray(sources) || sources.length === 0) {
    return null;
  }

  return (
    <div className="stack">
      <strong>Sources</strong>
      <div className="stack">
        {sources.map((source, index) => (
          <div key={`${source.url || source.title || "source"}-${index}`} className="info-text">
            <div><strong>{source.title || source.url || `Source ${index + 1}`}</strong></div>
            {source.publisher ? <div>{source.publisher}</div> : null}
            {source.url ? (
              <div>
                <a href={source.url} target="_blank" rel="noreferrer">
                  {source.url}
                </a>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function DemoPresentation({ presentation }) {
  if (!presentation || typeof presentation !== "object") {
    return null;
  }
  const h = presentation.headers || {};
  const excerpt = presentation.what_the_rules_say;
  const actions = presentation.next_best_actions || [];
  const why = presentation.why_this_answer;
  const who = presentation.who_should_act || [];
  const esc = presentation.when_to_escalate || [];

  const hasAny =
    (excerpt && excerpt.length > 0) ||
    actions.length > 0 ||
    (why && why.length > 0) ||
    who.length > 0 ||
    esc.length > 0;
  if (!hasAny) {
    return null;
  }

  return (
    <div className="stack" style={{ marginBottom: "0.75rem" }}>
      {excerpt ? (
        <div>
          <strong>{h.evidence || "What the rules say"}</strong>
          <div className="info-text" style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>
            {excerpt}
          </div>
        </div>
      ) : null}
      {actions.length ? (
        <div>
          <strong>{h.guidance || "What to do next"}</strong>
          <ul style={{ margin: "0.35rem 0 0 1.1rem" }}>
            {actions.map((line, i) => (
              <li key={`${i}-${line}`} className="info-text">
                {line}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {who.length ? (
        <div>
          <strong>Who should act</strong>
          <ul style={{ margin: "0.35rem 0 0 1.1rem" }}>
            {who.map((line, i) => (
              <li key={`w-${i}-${line}`} className="info-text">
                {line}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {esc.length ? (
        <div>
          <strong>When to escalate</strong>
          <ul style={{ margin: "0.35rem 0 0 1.1rem" }}>
            {esc.map((line, i) => (
              <li key={`e-${i}-${line}`} className="info-text">
                {line}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {why ? (
        <div>
          <strong>{h.reasoning || "Why this answer"}</strong>
          <div className="info-text" style={{ marginTop: 4 }}>
            {why}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function DeliveryPanel({ response, playbackEpoch = 0, onTtsPhaseChange, onPlaybackReady }) {
  const answer = response?.delivery?.answer;
  const mode = response?.delivery?.mode;
  const sources = response?.delivery?.sources || [];
  const proposalRecord = response?.proposal_record ?? null;
  const presentation = response?.presentation;
  const playbackKey = `${playbackEpoch}:${proposalRecord?.id ?? "noid"}:${(answer || "").length}`;

  if (!answer) {
    return (
      <div className="info-text">
        No delivered response yet.
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="info-text">
        <strong>Mode:</strong> {mode || "-"}
      </div>
      <DemoPresentation presentation={presentation} />
      <div className="info-text" style={{ whiteSpace: "pre-wrap" }}>
        {answer}
      </div>
      <MaloneAnswerPlayback
        answerText={answer}
        playbackKey={playbackKey}
        onTtsPhaseChange={onTtsPhaseChange}
        onPlaybackReady={onPlaybackReady}
      />
      <DeliverySources sources={sources} />
    </div>
  );
}

export default function ProposalPanel({
  response,
  recentProposals = [],
  playbackEpoch = 0,
  onTtsPhaseChange,
  onPlaybackReady,
}) {
  const proposalRecord = response?.proposal_record ?? null;

  return (
    <div className="card">
      <h3>Malone Output</h3>
      <p>This page now defaults to the delivered answer first. Technical proof and state are available only if you open the details.</p>

      <DeliveryPanel
        response={response}
        playbackEpoch={playbackEpoch}
        onTtsPhaseChange={onTtsPhaseChange}
        onPlaybackReady={onPlaybackReady}
      />

      {response ? (
        <details className="stack">
          <summary><strong>Show technical details</strong></summary>

          <div className="stack">
            <div className="info-text">
              <strong>Status:</strong> {response.status ?? "-"}
            </div>

            {proposalRecord ? (
              <div className="info-text">
                <strong>Persisted Proposal ID:</strong> {proposalRecord.id}
              </div>
            ) : null}

            <div>
              <strong>Intent</strong>
              <pre className="inline-json">{renderJson(response.intent)}</pre>
            </div>

            <div>
              <strong>Truth Packet</strong>
              <pre className="inline-json">{renderJson(response.truth_packet)}</pre>
            </div>

            <div>
              <strong>Rendered Output</strong>
              <pre className="inline-json">{renderJson(response.rendered_output)}</pre>
            </div>

            <div>
              <strong>Verification</strong>
              <pre className="inline-json">{renderJson(response.verification)}</pre>
            </div>

            {proposalRecord ? (
              <div>
                <strong>Persisted Record</strong>
                <pre className="inline-json">{renderJson(proposalRecord)}</pre>
              </div>
            ) : null}
          </div>
        </details>
      ) : null}

      <details className="stack">
        <summary><strong>Show recent proposals</strong></summary>
        <div className="stack">
          {recentProposals.length
            ? recentProposals.map(renderRecentProposal)
            : <div className="info-text">No persisted proposals yet.</div>}
        </div>
      </details>
    </div>
  );
}
