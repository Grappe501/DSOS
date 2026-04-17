# Malone Voice Phase 3 — STT / listen (browser-first)

**Date:** 2026-04-16  
**Scope:** Active lane (`app/`, `src/`, `tracking/`, `tests/`, `tools/`). No changes to `backend/`, `frontend/`, `dsos_replacements/`.

## 1. WHAT THIS PASS IMPLEMENTED

### Concrete STT/listen capabilities added

- **Explicit listen activation:** Push-to-talk style **Listen** control (start / stop listening). No always-on wake mode.
- **Browser Web Speech API path:** `SpeechRecognition` / `webkitSpeechRecognition` behind feature detection, with `continuous` + `interimResults` for near-live transcript preview.
- **Microphone preflight:** Optional `getUserMedia({ audio: true })` before starting recognition, with clear messages for denied / missing device / generic failure.
- **Transcript UX:** Read-only **Live transcript** while listening; after **Stop listening**, editable **Review and edit** textarea; **Send transcript** and **Cancel** before submit.
- **Single Malone chat path:** `useMaloneChatRequest` hook centralizes `maloneApi.chat(..., { signal })` for both typed **Send** and **Send transcript** (shared `AbortController` and sequence behavior with Phase 2 semantics).
- **Barge-in lite:** Starting listen calls registered playback `stopPlayback()` so active TTS fetch/audio stops before capture (deterministic; only when playback component has registered).
- **Voice session labels:** `deriveMaloneVoiceSessionState` extended with listen phases: `idle`, `listening`, `transcribing`, `ready_to_send`, `requesting`, `speaking`, `stopped`.

### What remained unchanged

- **Malone legal/text spine:** `POST /api/malone/chat` and server handling unchanged; no voice-specific reasoning route.
- **TTS:** `GET /api/malone/voice/status`, `POST /api/malone/tts`, ElevenLabs service unchanged.
- **Grounding:** Answers still come from the same `delivery.answer` and truth packet / evidence behavior.

## 2. HOW LISTEN MODE NOW WORKS

### Activation

User clicks **Listen** (after any mic permission flow). **Cancel listen** discards the session. **Listen** is disabled while a Malone request is in flight, while reviewing a transcript, or when STT is unsupported.

### Transcript flow

1. Optional mic preflight; then **Web Speech** starts after **Listen** (and after TTS stop hook).
2. Interim + final results build a **live** line in the read-only area; session may show **Transcribing** once speech is detected.
3. **Stop listening** ends recognition and opens **Review and edit** with combined text.

### Send/cancel behavior

- **Send transcript** calls the shared `submitMessage` (same as typing). On success, transcript UI clears.
- **Cancel** on review clears draft and exits listen flow. **Cancel listen** aborts capture without sending.

### Fallback behavior

- Unsupported browser: explanatory copy; typed chat remains primary.
- Mic denied / unavailable: error text; user can still type.
- Recognition errors: non-fatal message; user can edit or type.

## 3. HOW THIS FITS ONE MALONE PATH

- **Transcript reuses `maloneApi.chat`:** Implemented only through `useMaloneChatRequest` → `maloneApi.chat(text, { signal })`, identical to typed submit.
- **Legal/text grounding unchanged:** No client fork of retrieval, truth packet, or proposal logic; voice is input transport only.

## 4. HANDS-FREE READINESS STATUS

### What is now possible

- Explicit **listen → review → send** without typing, in supported browsers.
- **Interrupt** read-aloud when starting a new listen session (when playback control is registered).

### What still must happen before true “just call Malone up” behavior

- **Wake / always-on** activation and OS-level integration (explicitly out of scope for this phase).
- **Server-side STT** if enterprise key custody or browser STT is insufficient.
- **Duplex / streaming** conversation and long-session ergonomics.

## 5. IMPLEMENTATION GAPS

**Exact next pass (recommended):** Voice Phase 4 — deepen STT reliability (language selection, error recovery, optional server STT proxy), hands-free polish, and production telemetry for permission/STT failure rates.

## 6. HARD-FAIL COMPLIANCE CHECK

- **Passive roots:** No edits under `backend/`, `frontend/`, or `dsos_replacements/`.
- **No second voice Malone path:** No alternate chat route or parallel client for reasoning.
- **No premature always-on wake mode:** Only explicit **Listen**; no wake loop or background capture.

## Verification (this run)

- `python -m pytest tests -q`
- `python -m compileall app -q`
- `npm run build`
