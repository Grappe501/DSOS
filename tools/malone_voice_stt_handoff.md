# Malone voice — STT handoff (contract)

**Purpose:** Single integration rule for Voice Phase 3+ so spoken input never forks Malone.

1. **Transcript → same HTTP call as typing:** `maloneApi.chat(transcript, { signal })` via `useMaloneChatRequest` shared with `ChatPanel` (cancel superseded work; ignore stale completions).
2. **Playback:** Continue to read `delivery.answer` only via `MaloneAnswerPlayback` (grounded text already shown in `ProposalPanel`).
3. **Wake / listen UI:** May call into the same submit path as the chat form (programmatic “send” with a string), not a parallel `fetch` shape or alternate route.

This file is intentionally short; behavior is implemented in `src/lib/maloneVoiceSession.js` (`STT_HANDOFF_CONTRACT`), `src/hooks/useMaloneChatRequest.js`, and `src/components/malone/VoiceInputButton.jsx` (submit) + `ChatPanel.jsx` (typed submit).
