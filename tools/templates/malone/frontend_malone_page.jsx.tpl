import ChatPanel from "../components/malone/ChatPanel";
import ProposalPanel from "../components/malone/ProposalPanel";
import AgentRunPanel from "../components/malone/AgentRunPanel";
import VoiceInputButton from "../components/malone/VoiceInputButton";

export default function MalonePage() {{
  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1>Malone</h1>
          <p>Voice-first orchestration layer. AI proposes, deterministic core validates.</p>
        </div>
        <VoiceInputButton />
      </div>

      <div className="grid-two">
        <ChatPanel />
        <ProposalPanel />
      </div>

      <AgentRunPanel />
    </section>
  );
}}
