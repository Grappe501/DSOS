# Next Thread — After Voice Phase 1 (TTS)

## What shipped

- Server-side ElevenLabs TTS (`/api/malone/tts`) + status (`/api/malone/voice/status`).
- Malone page playback: Speak / Stop / Replay / Auto-read using **`delivery.answer`** text only.
- Tests: `tests/test_elevenlabs_service.py`.

## Configure locally

1. Set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` in the API process environment.
2. Restart FastAPI; open Malone; send a chat message; use **Speak answer**.

## Next: Voice Phase 2 — Interruption / control

**Goal:** Stop feeling clumsy — cancel in-flight HTTP, prevent overlapping/stale playback, align UI state.

**Suggested tasks:**

1. Plumb **`AbortController`** through `maloneApi.chat` and `maloneApi.tts` (optional `signal` already on `tts`).
2. On new chat submit: abort prior TTS fetch; stop `Audio` element.
3. Track **active proposal/response id** so an older response cannot start playback after a newer answer arrives.
4. Refine disabled/enabled rules for Stop during loading.

**Do not** add STT until Phase 2 is stable.

## Constraints

- Active lane only (`app/`, `src/`, `tracking/`, `tests/`, `tools/`).
- One Malone path — no voice-specific backend brain.
