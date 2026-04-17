# Malone Voice Phase 3 — Browser STT plan / contract

**Date:** 2026-04-16

## Goal

Provide **speech-to-text as input transport** only. Reasoning, grounding, and answer delivery stay on the existing Malone HTTP path.

## API surface

| Piece | Role |
|-------|------|
| `getSpeechRecognitionConstructor()` | Returns `SpeechRecognition` or `webkitSpeechRecognition` or `null`. |
| `isBrowserSttSupported()` | Boolean feature gate for UI. |
| `createSpeechRecognition({ lang, continuous, interimResults })` | Configured recognition instance or `null`. |

## Runtime expectations

- **Chromium** (Chrome, Edge): typically full support for `webkitSpeechRecognition`.
- **Firefox:** often **no** Web Speech recognition in stable builds — UI must degrade without breaking chat.
- **Safari:** variable; treat as best-effort with the same feature gate.

## Data contract

1. **Input to Malone:** Plain string (final or edited transcript), same as typed message.
2. **No parallel channel:** Do not add `POST /api/malone/voice/transcribe` for reasoning in this phase; optional future server STT is a **separate** decision.
3. **Abort semantics:** Same `AbortSignal` from `useMaloneChatRequest` as typed submit.

## Privacy / safety notes

- Recognition may use **vendor/cloud** backends depending on browser — document in UX (see `malone_voice_phase3_listen_ux.md`).
- **Explicit** user gesture (**Listen**) before capture; no passive listening in this phase.

## Barge-in

Before `recognition.start()`, call registered `stopPlayback()` from `MaloneAnswerPlayback` so TTS does not overlap new capture when an answer is playing.
