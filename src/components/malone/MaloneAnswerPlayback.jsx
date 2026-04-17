import { useCallback, useEffect, useRef, useState } from "react";
import { maloneApi } from "../../lib/maloneApi";
import { isAbortError } from "../../lib/maloneVoiceSession";

const AUTO_READ_KEY = "malone_tts_auto_read";

function loadAutoReadPreference() {
  try {
    return localStorage.getItem(AUTO_READ_KEY) === "1";
  } catch {
    return false;
  }
}

function saveAutoReadPreference(value) {
  try {
    localStorage.setItem(AUTO_READ_KEY, value ? "1" : "0");
  } catch {
    /* ignore */
  }
}

/**
 * Plays the same delivered answer text shown in the UI via server-side ElevenLabs TTS.
 * Voice Phase 2: TTS fetch abort; Phase 3: onPlaybackReady({ stopPlayback }) for STT barge-in.
 *
 * @param {{ answerText: string, playbackKey: string, onTtsPhaseChange?: (phase: 'silent'|'loading'|'playing'|'stopped') => void, onPlaybackReady?: (api: { stopPlayback: () => void } | null) => void }} props
 */
export default function MaloneAnswerPlayback({
  answerText,
  playbackKey,
  onTtsPhaseChange,
  onPlaybackReady,
}) {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [ttsAvailable, setTtsAvailable] = useState(null);
  const [autoRead, setAutoRead] = useState(loadAutoReadPreference);
  const [hasTrack, setHasTrack] = useState(false);

  const audioRef = useRef(null);
  const blobUrlRef = useRef(null);
  const lastFetchKeyRef = useRef(null);
  const lastAutoKeyRef = useRef(null);
  const ttsAbortRef = useRef(null);
  const playbackKeyRef = useRef(playbackKey);
  const autoRunTokenRef = useRef(0);

  const notifyTts = useCallback(
    (phase) => {
      onTtsPhaseChange?.(phase);
    },
    [onTtsPhaseChange],
  );

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const s = await maloneApi.voiceStatus();
        if (!cancelled) {
          setTtsAvailable(Boolean(s?.tts_configured));
        }
      } catch {
        if (!cancelled) {
          setTtsAvailable(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const releaseBlob = useCallback(() => {
    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current);
      blobUrlRef.current = null;
    }
    setHasTrack(false);
  }, []);

  const abortTtsFetch = useCallback(() => {
    ttsAbortRef.current?.abort();
    ttsAbortRef.current = null;
  }, []);

  const stop = useCallback(() => {
    abortTtsFetch();
    const a = audioRef.current;
    if (a) {
      a.pause();
      a.currentTime = 0;
    }
    setStatus("idle");
    notifyTts("stopped");
  }, [abortTtsFetch, notifyTts]);

  useEffect(() => {
    onPlaybackReady?.({ stopPlayback: stop });
    return () => {
      onPlaybackReady?.(null);
    };
  }, [stop, onPlaybackReady]);

  useEffect(() => {
    return () => {
      abortTtsFetch();
      const a = audioRef.current;
      if (a) {
        a.pause();
        a.currentTime = 0;
      }
      releaseBlob();
    };
  }, [abortTtsFetch, releaseBlob]);

  useEffect(() => {
    playbackKeyRef.current = playbackKey;
    autoRunTokenRef.current += 1;
    lastFetchKeyRef.current = null;
    lastAutoKeyRef.current = null;
    abortTtsFetch();
    const a = audioRef.current;
    if (a) {
      a.pause();
      a.currentTime = 0;
    }
    releaseBlob();
    setStatus("idle");
    setError("");
    notifyTts("silent");
  }, [playbackKey, abortTtsFetch, releaseBlob, notifyTts]);

  const ensureAudio = useCallback(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.addEventListener("ended", () => {
        setStatus("idle");
        notifyTts("silent");
      });
      audioRef.current.addEventListener("error", () => {
        setError("Audio playback failed.");
        setStatus("idle");
        notifyTts("silent");
      });
    }
    return audioRef.current;
  }, [notifyTts]);

  const fetchAndPlay = useCallback(
    async (isAuto) => {
      const text = (answerText || "").trim();
      if (!text) {
        setError("Nothing to speak yet.");
        return;
      }
      if (ttsAvailable === false) {
        setError("TTS is not configured on the server.");
        return;
      }

      const tokenAtStart = autoRunTokenRef.current;
      const keyAtStart = playbackKeyRef.current;

      setError("");
      setStatus("loading");
      notifyTts("loading");

      const cacheKey = `${playbackKey || "k"}:${text}`;
      abortTtsFetch();
      const ac = new AbortController();
      ttsAbortRef.current = ac;

      try {
        if (!(lastFetchKeyRef.current === cacheKey && blobUrlRef.current)) {
          releaseBlob();
          lastFetchKeyRef.current = cacheKey;
          const blob = await maloneApi.tts(text, { signal: ac.signal });
          if (tokenAtStart !== autoRunTokenRef.current || keyAtStart !== playbackKeyRef.current) {
            return;
          }
          const url = URL.createObjectURL(blob);
          blobUrlRef.current = url;
          setHasTrack(true);
        }

        if (tokenAtStart !== autoRunTokenRef.current || keyAtStart !== playbackKeyRef.current) {
          return;
        }

        const audio = ensureAudio();
        audio.src = blobUrlRef.current;
        await audio.play();
        ttsAbortRef.current = null;
        if (tokenAtStart !== autoRunTokenRef.current || keyAtStart !== playbackKeyRef.current) {
          audio.pause();
          audio.currentTime = 0;
          return;
        }
        setStatus("playing");
        notifyTts("playing");
      } catch (err) {
        if (isAbortError(err)) {
          return;
        }
        const msg =
          err instanceof Error && err.message ? err.message : "Could not load speech audio.";
        if (tokenAtStart !== autoRunTokenRef.current || keyAtStart !== playbackKeyRef.current) {
          return;
        }
        setError(msg);
        setStatus("idle");
        notifyTts("silent");
        if (!isAuto) {
          lastFetchKeyRef.current = null;
        }
      }
    },
    [answerText, playbackKey, ttsAvailable, ensureAudio, releaseBlob, abortTtsFetch, notifyTts],
  );

  const onPlay = () => {
    void fetchAndPlay(false);
  };

  const onReplay = () => {
    if (!hasTrack) {
      return;
    }
    const tokenAtStart = autoRunTokenRef.current;
    const keyAtStart = playbackKeyRef.current;
    const audio = ensureAudio();
    audio.currentTime = 0;
    void audio
      .play()
      .then(() => {
        if (tokenAtStart !== autoRunTokenRef.current || keyAtStart !== playbackKeyRef.current) {
          audio.pause();
          audio.currentTime = 0;
          return;
        }
        setStatus("playing");
        notifyTts("playing");
      })
      .catch(() => {
        setStatus("idle");
        notifyTts("silent");
      });
  };

  useEffect(() => {
    if (!autoRead) {
      return;
    }
    const text = (answerText || "").trim();
    if (!text) {
      return;
    }
    const k = `${playbackKey || text}`;
    if (lastAutoKeyRef.current === k) {
      return;
    }
    lastAutoKeyRef.current = k;
    void fetchAndPlay(true);
  }, [answerText, playbackKey, autoRead, fetchAndPlay]);

  const toggleAutoRead = () => {
    const next = !autoRead;
    setAutoRead(next);
    saveAutoReadPreference(next);
    if (!next) {
      stop();
      lastAutoKeyRef.current = null;
    }
  };

  const baseDisabled =
    ttsAvailable === false || ttsAvailable === null || !(answerText || "").trim();

  return (
    <div className="stack" style={{ marginTop: "0.75rem" }}>
      <div
        className="info-text"
        style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}
      >
        <strong>Voice (read aloud)</strong>
        {ttsAvailable === false ? (
          <span className="info-text">TTS unavailable (server not configured).</span>
        ) : null}
        {ttsAvailable === null ? <span className="info-text">Checking TTS…</span> : null}
        <label
          className="info-text"
          style={{ display: "inline-flex", gap: "0.35rem", alignItems: "center" }}
        >
          <input type="checkbox" checked={autoRead} onChange={toggleAutoRead} disabled={baseDisabled} />
          Auto-read new answers
        </label>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
        <button
          className="secondary-button"
          type="button"
          onClick={onPlay}
          disabled={baseDisabled || status === "loading"}
        >
          {status === "loading" ? "Loading…" : status === "playing" ? "Playing…" : "Speak answer"}
        </button>
        <button
          className="secondary-button"
          type="button"
          onClick={stop}
          disabled={status === "idle"}
          title="Stop playback and cancel in-flight TTS fetch."
        >
          Stop
        </button>
        <button
          className="secondary-button"
          type="button"
          onClick={onReplay}
          disabled={baseDisabled || !hasTrack}
        >
          Replay
        </button>
      </div>

      {error ? <div className="error-text">{error}</div> : null}
    </div>
  );
}
