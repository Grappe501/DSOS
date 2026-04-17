import { useCallback, useEffect, useRef, useState } from "react";
import { createSpeechRecognition, isBrowserSttSupported } from "../../lib/maloneBrowserSpeech";
import { describeMicBlockReason, requestMicPermissionPreview } from "../../lib/micCapability";

/** @typedef {'none'|'listening'|'transcribing'|'ready_to_send'} ListenPhase */

/**
 * Explicit browser STT (Web Speech API). Transcript submit uses the same Malone chat path as typing.
 *
 * @param {{
 *   voiceSessionLabel?: string,
 *   chatLoading?: boolean,
 *   onBeforeListenStart?: () => void,
 *   onListenPhaseChange?: (phase: ListenPhase) => void,
 *   submitMessage: (text: string) => Promise<boolean>,
 * }} props
 */
export default function VoiceInputButton({
  voiceSessionLabel = "—",
  chatLoading = false,
  onBeforeListenStart,
  onListenPhaseChange,
  submitMessage,
}) {
  const [listenPhase, setListenPhase] = useState(/** @type {ListenPhase} */ ("none"));
  const [sttBlockedReason, setSttBlockedReason] = useState("");
  const [livePreview, setLivePreview] = useState("");
  const [draft, setDraft] = useState("");
  const [localError, setLocalError] = useState("");

  const recognitionRef = useRef(null);
  const finalBufferRef = useRef("");
  const interimRef = useRef("");
  const discardOnEndRef = useRef(false);

  const setPhase = useCallback(
    (next) => {
      setListenPhase(next);
      onListenPhaseChange?.(next);
    },
    [onListenPhaseChange],
  );

  const teardownRecognition = useCallback(() => {
    const rec = recognitionRef.current;
    recognitionRef.current = null;
    if (!rec) {
      return;
    }
    rec.onresult = null;
    rec.onerror = null;
    rec.onend = null;
    try {
      rec.stop();
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    return () => {
      discardOnEndRef.current = true;
      teardownRecognition();
    };
  }, [teardownRecognition]);

  const resetListenBuffers = useCallback(() => {
    finalBufferRef.current = "";
    interimRef.current = "";
    setLivePreview("");
  }, []);

  const beginListening = useCallback(async () => {
    if (chatLoading) {
      setLocalError("Wait for the current Malone request to finish, or cancel it.");
      return;
    }
    setSttBlockedReason("");
    setLocalError("");

    if (!isBrowserSttSupported()) {
      setSttBlockedReason(
        "Speech recognition is not available in this browser. Use Chrome or Edge, or type your request.",
      );
      return;
    }

    const mic = await requestMicPermissionPreview();
    if (!mic.ok) {
      setSttBlockedReason(describeMicBlockReason(mic));
      return;
    }

    onBeforeListenStart?.();

    resetListenBuffers();
    discardOnEndRef.current = false;

    const rec = createSpeechRecognition({ continuous: true, interimResults: true });
    if (!rec) {
      setSttBlockedReason("Could not create speech recognition. Type your request instead.");
      return;
    }

    rec.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const piece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalBufferRef.current += piece;
        } else {
          interim += piece;
        }
      }
      interimRef.current = interim;
      const combined = `${finalBufferRef.current}${interim}`.trim();
      setLivePreview(combined);
      if (interim || finalBufferRef.current) {
        setPhase("transcribing");
      }
    };

    rec.onerror = (event) => {
      if (event.error === "aborted") {
        return;
      }
      if (event.error === "no-speech") {
        return;
      }
      setLocalError(
        `Speech recognition reported “${event.error || "error"}”. You can edit text below or type in the message box.`,
      );
    };

    rec.onend = () => {
      recognitionRef.current = null;
      if (discardOnEndRef.current) {
        discardOnEndRef.current = false;
        resetListenBuffers();
        setPhase("none");
        return;
      }
      const text = `${finalBufferRef.current}${interimRef.current}`.trim();
      resetListenBuffers();
      setDraft(text);
      setPhase("ready_to_send");
    };

    recognitionRef.current = rec;

    try {
      setPhase("listening");
      rec.start();
    } catch {
      setLocalError("Could not start listening. Try again or type your request.");
      recognitionRef.current = null;
      setPhase("none");
    }
  }, [chatLoading, onBeforeListenStart, resetListenBuffers, setPhase]);

  const stopListeningForReview = useCallback(() => {
    if (!recognitionRef.current) {
      return;
    }
    try {
      recognitionRef.current.stop();
    } catch {
      /* ignore */
    }
  }, []);

  const cancelWhileListening = useCallback(() => {
    discardOnEndRef.current = true;
    teardownRecognition();
    resetListenBuffers();
    setPhase("none");
    setLocalError("");
  }, [resetListenBuffers, setPhase, teardownRecognition]);

  const cancelReview = useCallback(() => {
    setDraft("");
    setPhase("none");
    setLocalError("");
  }, [setPhase]);

  const sendTranscript = useCallback(async () => {
    const text = draft.trim();
    if (!text) {
      setLocalError("Nothing to send. Speak again, edit the text, or type in the message box.");
      return;
    }
    setLocalError("");
    const ok = await submitMessage(text);
    if (ok) {
      setDraft("");
      setPhase("none");
    }
  }, [draft, submitMessage, setPhase]);

  const listeningActive = listenPhase === "listening" || listenPhase === "transcribing";
  const inReview = listenPhase === "ready_to_send";
  const sttUnavailable = !isBrowserSttSupported();

  const listenToggleLabel = listeningActive ? "Stop listening" : "Listen";
  const listenDisabled = chatLoading || sttUnavailable || inReview;

  return (
    <div
      className="stack"
      style={{ alignItems: "flex-end", gap: "0.35rem", minWidth: "14rem", maxWidth: "22rem" }}
    >
      <div className="info-text" style={{ fontSize: "0.85rem", textAlign: "right" }}>
        Voice session: <strong>{voiceSessionLabel}</strong>
      </div>

      {sttBlockedReason ? (
        <div className="error-text" style={{ fontSize: "0.85rem", textAlign: "right" }}>
          {sttBlockedReason}
        </div>
      ) : null}

      {sttUnavailable ? (
        <div className="info-text" style={{ fontSize: "0.85rem", textAlign: "right" }}>
          Speech-to-text needs a supported browser (for example Chrome or Edge). Typed input always works.
        </div>
      ) : null}

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", justifyContent: "flex-end" }}>
        <button
          className={listeningActive ? "secondary-button" : "primary-button"}
          type="button"
          title={
            sttUnavailable
              ? "Speech recognition is not supported in this browser."
              : "Start or stop microphone listening (push-to-talk). Stops read-aloud if playing."
          }
          disabled={listenDisabled}
          onClick={() => {
            if (listeningActive) {
              stopListeningForReview();
            } else {
              void beginListening();
            }
          }}
        >
          {listenToggleLabel}
        </button>
        {listeningActive ? (
          <button
            className="secondary-button"
            type="button"
            title="Discard this listen session without sending."
            onClick={cancelWhileListening}
          >
            Cancel listen
          </button>
        ) : null}
      </div>

      {listeningActive ? (
        <div className="stack" style={{ width: "100%", alignItems: "stretch" }}>
          <label className="info-text" htmlFor="malone-live-transcript" style={{ fontSize: "0.8rem" }}>
            Live transcript
          </label>
          <textarea
            id="malone-live-transcript"
            readOnly
            value={livePreview}
            placeholder="Speak after clicking Listen. Your words appear here."
            rows={3}
            style={{ width: "100%", opacity: 0.95 }}
          />
        </div>
      ) : null}

      {inReview ? (
        <div className="stack" style={{ width: "100%", alignItems: "stretch" }}>
          <label className="info-text" htmlFor="malone-voice-draft" style={{ fontSize: "0.8rem" }}>
            Review and edit before sending to Malone
          </label>
          <textarea
            id="malone-voice-draft"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={4}
            style={{ width: "100%" }}
            disabled={chatLoading}
          />
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", justifyContent: "flex-end" }}>
            <button
              className="primary-button"
              type="button"
              disabled={chatLoading || !draft.trim()}
              onClick={() => void sendTranscript()}
            >
              Send transcript
            </button>
            <button
              className="secondary-button"
              type="button"
              disabled={chatLoading}
              onClick={cancelReview}
            >
              Cancel
            </button>
          </div>
        </div>
      ) : null}

      {localError ? (
        <div className="error-text" style={{ fontSize: "0.85rem", textAlign: "right" }}>
          {localError}
        </div>
      ) : null}
    </div>
  );
}
