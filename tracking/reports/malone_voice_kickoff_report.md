# Malone Voice Kickoff — Post Phase 6

**Date:** 2026-04-16  
**Scope:** Active lane (`app/`, `src/`, `tracking/`, `tests/`, `tools/`). No changes to `backend/`, `frontend/`, `dsos_replacements/`.

## Mission

Begin the **voice workstream** as an **interface + transport + playback** layer on the **same Malone path**. Legal phases 0–6 are assumed complete; voice does not fork Malone.

## What this kickoff implemented

### Voice Phase 1 — TTS foundation (implemented)

1. **Server-side ElevenLabs** — `app/services/elevenlabs_service.py` calls ElevenLabs REST TTS with `xi-api-key`; no key in the browser.
2. **Authenticated API** — `GET /api/malone/voice/status`, `POST /api/malone/tts` in `app/api/malone_routes.py` (same auth as Malone chat).
3. **Playback UI** — `src/components/malone/MaloneAnswerPlayback.jsx`: Speak answer, Stop, Replay, Auto-read (persisted in `localStorage`).
4. **Same text as UI** — Playback uses `delivery.answer` already shown in `ProposalPanel`.
5. **Audit** — `malone.tts.completed` rows in `audit_logs` with lengths and byte counts (no raw text).
6. **Mic stub** — `VoiceInputButton` labeled as STT deferred; disabled so it does not imply STT exists.

### Not built (deferred)

- STT / push-to-talk (Voice Phase 3).
- Fetch `AbortController` / stale playback hardening (Voice Phase 2).
- Streaming / full duplex.

## Verification (this run)

- `python -m pytest tests -q` — pass  
- `python -m compileall app -q` — pass  
- `npm run build` — pass  

## Configuration

See `malone_voice_phase1_config_plan.md` and `malone_voice_phase1_elevenlabs_execution.md`.

## Next recommendation

**Voice Phase 2** — chat request cancellation + playback interruption and stale-response guards (see `NEXT_THREAD_PROMPT_VOICE_PHASE1.md`).
