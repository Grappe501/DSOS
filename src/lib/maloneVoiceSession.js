/**
 * Voice control layer: single Malone spine — this module only models UI/session state
 * and contracts for STT. No alternate Malone pipeline.
 */

/**
 * @typedef {'idle'|'listening'|'transcribing'|'ready_to_send'|'requesting'|'speaking'|'stopped'} MaloneVoiceSessionState
 */

export const MALONE_VOICE_SESSION = {
  IDLE: "idle",
  LISTENING: "listening",
  TRANSCRIBING: "transcribing",
  READY_TO_SEND: "ready_to_send",
  REQUESTING: "requesting",
  SPEAKING: "speaking",
  STOPPED: "stopped",
};

/**
 * @typedef {'silent'|'loading'|'playing'|'stopped'} TtsPlaybackPhase
 * - silent: no TTS activity for the current answer
 * - loading: fetching or preparing MP3 for this answer
 * - playing: audio output active
 * - stopped: user interrupted playback (until new answer or new speak)
 */

/**
 * listenPhase from STT UI: none when not in a listen/review flow.
 * @typedef {'none'|'listening'|'transcribing'|'ready_to_send'} MaloneListenPhase
 */

/**
 * Derive a single high-level voice session label for the Malone page chrome.
 * Priority: chat in flight > transcript review > listen > TTS > idle.
 * @param {{ chatBusy: boolean, ttsPhase: TtsPlaybackPhase, listenPhase?: MaloneListenPhase }} p
 * @returns {MaloneVoiceSessionState}
 */
export function deriveMaloneVoiceSessionState({ chatBusy, ttsPhase, listenPhase = "none" }) {
  if (chatBusy) {
    return MALONE_VOICE_SESSION.REQUESTING;
  }
  if (listenPhase === "ready_to_send") {
    return MALONE_VOICE_SESSION.READY_TO_SEND;
  }
  if (listenPhase === "listening") {
    return MALONE_VOICE_SESSION.LISTENING;
  }
  if (listenPhase === "transcribing") {
    return MALONE_VOICE_SESSION.TRANSCRIBING;
  }
  if (ttsPhase === "loading" || ttsPhase === "playing") {
    return MALONE_VOICE_SESSION.SPEAKING;
  }
  if (ttsPhase === "stopped") {
    return MALONE_VOICE_SESSION.STOPPED;
  }
  return MALONE_VOICE_SESSION.IDLE;
}

export function isAbortError(err) {
  return Boolean(err && typeof err === "object" && err.name === "AbortError");
}

/**
 * STT handoff: spoken text must enter the same path as typed text —
 * `maloneApi.chat(transcript, { signal })` with the same AbortController policy as shared chat hook.
 */
export const STT_HANDOFF_CONTRACT = {
  chatEntry: "maloneApi.chat(text, { signal })",
  abortSharedWith: "useMaloneChatRequest (MalonePage) — shared with ChatPanel",
};

/**
 * Placeholder for wake-style activation (not used in Phase 3 explicit listen).
 */
export function createWakeActivationStub() {
  return {
    /** @returns {void} */
    notifyReadyForVoiceIntent() {
      /* Future: optional wake pipeline. */
    },
  };
}

const VOICE_SESSION_LABELS = {
  [MALONE_VOICE_SESSION.IDLE]: "Idle",
  [MALONE_VOICE_SESSION.LISTENING]: "Listening",
  [MALONE_VOICE_SESSION.TRANSCRIBING]: "Transcribing",
  [MALONE_VOICE_SESSION.READY_TO_SEND]: "Review transcript",
  [MALONE_VOICE_SESSION.REQUESTING]: "Requesting",
  [MALONE_VOICE_SESSION.SPEAKING]: "Speaking",
  [MALONE_VOICE_SESSION.STOPPED]: "Stopped (playback)",
};

export function formatVoiceSessionLabel(state) {
  return VOICE_SESSION_LABELS[state] ?? state;
}
