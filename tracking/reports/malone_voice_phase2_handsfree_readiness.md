# Malone Voice Phase 2 — Hands-Free Readiness

**Date:** 2026-04-16

## Completed in Phase 2 (control foundation)

- **Interruptibility:** Chat and TTS can be aborted; UI reflects **requesting** vs **speaking** vs **stopped**.
- **Coherence:** Latest answer identity drives playback; old audio cannot “win” after a new response.
- **Contract for STT:** `STT_HANDOFF_CONTRACT` in `src/lib/maloneVoiceSession.js` — transcripts must use `maloneApi.chat` with the same abort semantics as `ChatPanel`.
- **Operator visibility:** Voice session label supports future trust UX when mic/listen are added.

## Still required for Alexa-like hands-free (not done here)

| Capability | Notes |
|------------|--------|
| Microphone access | Explicit permission UX; likely `getUserMedia` (Phase 3). |
| Speech-to-text | Client SDK or server proxy; output **string** only. |
| Listen session | Pair “listening” UI with **one** in-flight chat `AbortController`. |
| Wake / activation | OS or push-to-open; avoid fragile browser always-on wake in early phases. |
| Barge-in | Natural extension of Phase 2 abort: STT start aborts TTS (future). |

## Recommended order

1. Push-to-talk or tap-to-talk **STT** → same chat path (Phase 3).  
2. **Barge-in:** speaking + new utterance aborts TTS using existing hooks.  
3. Optional **wake** once interrupt semantics are proven in production-like use.
