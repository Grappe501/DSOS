import { useEffect, useState } from "react";
import ChatPanel from "../components/malone/ChatPanel";
import ProposalPanel from "../components/malone/ProposalPanel";
import VoiceInputButton from "../components/malone/VoiceInputButton";
import { maloneApi } from "../lib/maloneApi";

export default function MalonePage() {
  const [response, setResponse] = useState(null);
  const [recentProposals, setRecentProposals] = useState([]);

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

    loadRecent();
    return () => {
      cancelled = true;
    };
  }, []);

  function handleResponse(nextResponse) {
    setResponse(nextResponse);

    const persisted = nextResponse?.proposal_record;
    if (!persisted?.id) {
      return;
    }

    setRecentProposals((current) => {
      const withoutDuplicate = current.filter((row) => row.id !== persisted.id);
      return [persisted, ...withoutDuplicate].slice(0, 12);
    });
  }

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1>Malone</h1>
          <p>
            Ask Malone a question and get a governed answer first. Technical proof stays tucked away unless you need it.
          </p>
        </div>
        <VoiceInputButton />
      </div>

      <div className="stack">
        <ChatPanel onResponse={handleResponse} />
        <ProposalPanel response={response} recentProposals={recentProposals} />
      </div>
    </section>
  );
}