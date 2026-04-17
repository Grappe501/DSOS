import { useCallback, useRef, useState } from "react";
import { maloneApi } from "../lib/maloneApi";
import { isAbortError } from "../lib/maloneVoiceSession";

/**
 * Single Malone chat HTTP path for typed and voice (STT) submit — shared AbortController policy.
 * @param {{ onResponse?: (data: unknown) => void }} options
 */
export function useMaloneChatRequest({ onResponse }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const abortRef = useRef(null);
  const seqRef = useRef(0);

  const cancelInFlight = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const cancelRequest = useCallback(() => {
    cancelInFlight();
    seqRef.current += 1;
    setLoading(false);
    setError("");
  }, [cancelInFlight]);

  const submitMessage = useCallback(
    async (rawText) => {
      const nextMessage = (rawText || "").trim();
      if (!nextMessage) {
        setError("Please enter a request for Malone.");
        return false;
      }

      cancelInFlight();
      const controller = new AbortController();
      abortRef.current = controller;
      const mySeq = (seqRef.current += 1);

      setLoading(true);
      setError("");

      try {
        const data = await maloneApi.chat(nextMessage, { signal: controller.signal });
        if (mySeq !== seqRef.current) {
          return false;
        }
        onResponse?.(data);
        return true;
      } catch (err) {
        if (isAbortError(err)) {
          if (mySeq === seqRef.current) {
            setError("");
          }
          return false;
        }
        const nextError =
          err instanceof Error && err.message ? err.message : "Malone request failed";
        if (mySeq !== seqRef.current) {
          return false;
        }
        setError(nextError);
        return false;
      } finally {
        if (mySeq === seqRef.current) {
          setLoading(false);
          abortRef.current = null;
        }
      }
    },
    [onResponse, cancelInFlight],
  );

  return {
    loading,
    error,
    setError,
    submitMessage,
    cancelRequest,
  };
}
