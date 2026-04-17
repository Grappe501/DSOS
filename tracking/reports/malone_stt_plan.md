# Malone Voice — Speech-to-Text (STT) Plan

**Date:** 2026-04-16  
**Principle:** STT produces a **plain string** fed into the existing `POST /api/malone/chat` path — same as typing.

---

## Current repo state

- No STT routes or services in `app/`.
- No `MediaRecorder` / Web Speech API usage in Malone components (see `tracking/reports/malone_voice_inventory.md`).
- `VoiceInputButton.jsx` is a non-interactive stub.

---

## Options (smallest to largest)

### Option A — Web Speech API (browser)

- **Pros:** No new backend, fastest V1, no audio upload pipeline.
- **Cons:** Browser support variance, needs HTTPS/localhost, quality varies, may not meet enterprise policy.

### Option B — Server-side STT (multipart upload)

- **Pros:** Consistent models, better governance, can log consent flows.
- **Cons:** New route, file size limits, storage policy, more moving parts.

### Option C — Vendor streaming STT (WebSocket)

- **Pros:** Lower latency, partial transcripts.
- **Cons:** Largest implementation; contradicts “no major architecture rewrite” for early phases.

---

## Recommended sequence

1. **Transcript UX first** — Even before STT, allow **paste-to-talk** or **editable transcript field** to validate the Malone flow with audio output only.
2. **Option A** behind feature detection — if `webkitSpeechRecognition` / `SpeechRecognition` unavailable, show “Type instead”.
3. **Option B** when compliance requires server-side processing.

---

## Mic capture checklist (when implemented)

- [ ] Permission prompt and denial handling
- [ ] Visual **listening** state
- [ ] **Editable** final transcript before send
- [ ] Clear error strings (no silent failure)

---

## Malone contract

- STT output = **`message` string** in `MaloneChatRequest`.
- No change to `handle_malone_request` signature.
