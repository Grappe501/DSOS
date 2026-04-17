import { useCallback, useEffect, useRef, useState } from "react";
import ChatPanel from "../components/malone/ChatPanel";
import MaloneInspectionPanel from "../components/malone/MaloneInspectionPanel";
import MaloneReviewPanel from "../components/malone/MaloneReviewPanel";
import DepartmentIntakePanel from "../components/malone/DepartmentIntakePanel";
import ProposalPanel from "../components/malone/ProposalPanel";
import VoiceInputButton from "../components/malone/VoiceInputButton";
import { useMaloneChatRequest } from "../hooks/useMaloneChatRequest";
import { maloneApi } from "../lib/maloneApi";
import {
  deriveMaloneVoiceSessionState,
  formatVoiceSessionLabel,
} from "../lib/maloneVoiceSession";

export default function MalonePage() {
  const [response, setResponse] = useState(null);
  const [demoFlags, setDemoFlags] = useState(null);
  const [recentProposals, setRecentProposals] = useState([]);
  const [playbackEpoch, setPlaybackEpoch] = useState(0);
  const [ttsPhase, setTtsPhase] = useState("silent");
  const [listenPhase, setListenPhase] = useState("none");

  const playbackControlRef = useRef(null);

  const handleResponse = useCallback((nextResponse) => {
    if (!nextResponse) {
      return;
    }

    setPlaybackEpoch((e) => e + 1);
    setResponse(nextResponse);

    const persisted = nextResponse?.proposal_record;
    if (!persisted?.id) {
      return;
    }

    setRecentProposals((current) => {
      const withoutDuplicate = current.filter((row) => row.id !== persisted.id);
      return [persisted, ...withoutDuplicate].slice(0, 12);
    });
  }, []);

  const chat = useMaloneChatRequest({ onResponse: handleResponse });

  useEffect(() => {
    let cancelled = false;

    async function loadRecent() {
      try {
        const rows = await maloneApi.getRecentProposals(12);
        if (!cancelled) {
          setRecentProposals(Array.isArray(rows) ? rows : []);
        }
      } catch {
        if (!cancelled) {
          setRecentProposals([]);
        }
      }
    }

    async function loadDemo() {
      try {
        const d = await maloneApi.getDemoStatus();
        if (!cancelled && d && typeof d === "object") {
          setDemoFlags(d);
        }
      } catch {
        if (!cancelled) {
          setDemoFlags(null);
        }
      }
    }

    void loadRecent();
    void loadDemo();
    return () => {
      cancelled = true;
    };
  }, []);

  const voiceState = deriveMaloneVoiceSessionState({
    chatBusy: chat.loading,
    ttsPhase,
    listenPhase,
  });
  const voiceSessionLabel = formatVoiceSessionLabel(voiceState);

  const handlePlaybackReady = useCallback((api) => {
    playbackControlRef.current = api;
  }, []);

  const onBeforeListenStart = useCallback(() => {
    playbackControlRef.current?.stopPlayback?.();
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1 style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.5rem" }}>
            Malone
            {demoFlags?.malone_demo_mode ? (
              <span
                title="Server MALONE_DEMO_MODE is on: tighter demo presentation and optional limited scope."
                style={{
                  fontSize: "0.65rem",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.04em",
                  padding: "0.2rem 0.45rem",
                  borderRadius: 6,
                  border: "1px solid #6cf6",
                  background: "#1a2330",
                }}
              >
                Demo mode
              </span>
            ) : null}
          </h1>
          <p>
            Ask Malone a question and get a governed answer first. Technical proof stays tucked away unless you need it.
          </p>
        </div>
        <VoiceInputButton
          voiceSessionLabel={voiceSessionLabel}
          chatLoading={chat.loading}
          onBeforeListenStart={onBeforeListenStart}
          onListenPhaseChange={setListenPhase}
          submitMessage={chat.submitMessage}
        />
      </div>

      <div className="stack">
        <ChatPanel chat={chat} demoActive={Boolean(demoFlags?.malone_demo_mode)} />
        <ProposalPanel
          response={response}
          recentProposals={recentProposals}
          playbackEpoch={playbackEpoch}
          onTtsPhaseChange={setTtsPhase}
          onPlaybackReady={handlePlaybackReady}
        />
        <MaloneInspectionPanel response={response} />
        <MaloneReviewPanel response={response} />
        <DepartmentIntakePanel demoActive={Boolean(demoFlags?.malone_demo_mode)} />
      </div>
    </section>
  );
}
