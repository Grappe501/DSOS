# Malone Voice Phase 2 — Interruption / Control + Hands-Free Readiness

**Date:** 2026-04-16  
**Scope:** Active lane (`app/`, `src/`, `tracking/`, `tests/`, `tools/`). No changes to `backend/`, `frontend/`, `dsos_replacements/`.

## 1. WHAT THIS PASS IMPLEMENTED

### Concrete interruption/control capabilities added

- **Chat HTTP cancellation:** `maloneApi.chat(message, { signal })` passes `AbortSignal` through `fetch`. `ChatPanel` uses a per-request `AbortController`, cancels the previous in-flight chat when a new send starts, exposes **Cancel request**, and uses a **sequence guard** so late completions from superseded requests do not update UI state.
- **TTS fetch cancellation:** `MaloneAnswerPlayback` aborts in-flight `POST /api/malone/tts` via `AbortController`, including when **Stop** is pressed, when a new fetch starts, or when the answer identity (`playbackKey`) changes.
- **Stale playback protection:** `playbackKey` includes `playbackEpoch` (incremented on each accepted chat response) plus proposal id and answer length token; in-flight TTS and `audio.play()` completions check tokens before applying state.
- **Playback coherence:** Only one TTS fetch and one play path per answer; overlapping audio from an older answer is prevented by abort + key checks.
- **Voice session model:** `deriveMaloneVoiceSessionState` maps chat busy + TTS phase to `idle | requesting | speaking | stopped | ready_for_input`. **VoiceInputButton** shows the label (keyboard/mouse and deferred mic/listen controls unchanged in spirit).
- **Hands-free hooks (scaffolding):** `maloneVoiceSession.js` documents `STT_HANDOFF_CONTRACT` and `createWakeActivationStub`; `tools/malone_voice_stt_handoff.md` states the single-chat-entry rule for Phase 3+.

### What remained unchanged

- **Malone legal/text spine:** `POST /api/malone/chat` → `handle_malone_request` unchanged; no second “voice Malone” route or client.
- **TTS server:** `GET /api/malone/voice/status`, `POST /api/malone/tts`, ElevenLabs service unchanged.
- **Grounding:** Answers still come from the same `delivery.answer` shown in the UI; playback reads that text only.

## 2. HOW VOICE CONTROL NOW WORKS

### Request cancellation

- Each send creates a new `AbortController`; a new send or **Cancel request** aborts the prior `fetch`. Aborts do not clear the last successful Malone response.

### Playback cancellation

- **Stop** aborts the TTS `fetch`, pauses `Audio`, and sets TTS phase to `stopped` (user-visible session state). Late MP3 bytes from an aborted request are not played.

### Stale-response handling

- **Chat:** Sequence number ensures only the latest request’s completion calls `onResponse`.
- **TTS:** `autoRunTokenRef` and `playbackKeyRef` guard `blob()` resolution and `audio.play()` after await.

### State machine behavior

- **requesting:** `chatBusy` true.
- **speaking:** TTS phase `loading` or `playing`.
- **stopped:** User stopped playback (`ttsPhase === stopped`) until a new answer or new speak cycle resets via `playbackKey` / phase updates.
- **ready_for_input:** Not requesting, not speaking, and an answer exists.
- **idle:** No answer yet and not requesting.

## 3. HANDS-FREE READINESS STATUS

### What now exists that makes “call Malone up” possible later

- Explicit **cancel** and **staleness** semantics for both chat and TTS—required before always-listening or wake-style UX is safe.
- A **single documented STT handoff contract** (same `maloneApi.chat` + same abort policy).
- **Visible voice session** label for user trust and debugging.

### What is still missing before true Alexa-like use

- Browser **microphone** capture, **STT**, and push-to-talk or managed listen sessions.
- **Wake-word** engine or OS-level activation (not shipped here by design).
- **Full-duplex** or streaming audio (out of scope).

## 4. MALONE INTEGRATION BOUNDARY

- **One Malone path only:** User input remains typed chat → `maloneApi.chat`; output remains `delivery.answer` → optional TTS. No parallel Malone stack.
- **Legal/text grounding unchanged:** No change to truth packets, evidence, citations, or proposal persistence logic in this pass.

## 5. IMPLEMENTATION GAPS

**Exact next pass (recommended):** **Voice Phase 3 — STT / listen session:** wire browser capture behind explicit user gesture, stream or batch transcript into `maloneApi.chat` with the same `AbortController` pattern, and define listen-mode UX using `VoiceInputButton` + session label. Optional: server-side STT proxy if keys must stay off the client.

## 6. HARD-FAIL COMPLIANCE CHECK

- **Passive roots:** No edits under `backend/`, `frontend/`, or `dsos_replacements/`.
- **No wholesale Malone replacement:** Chat and reasoning path untouched server-side except existing routes.
- **No speculative always-on wake engine:** No wake-word loop, no always-on mic; only control-layer and documented contracts.

## Verification (this run)

- `python -m pytest tests -q` — pass  
- `python -m compileall app -q` — pass  
- `npm run build` — pass  
