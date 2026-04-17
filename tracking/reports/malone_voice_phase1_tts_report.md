# Malone Voice Phase 1 — TTS Foundation

**Status:** Complete  
**Date:** 2026-04-16

## Goal

Malone can **speak grounded answer text** aloud using **ElevenLabs** behind an **authenticated server proxy**, without exposing API keys to the SPA.

## Build summary

| Area | Deliverable |
|------|-------------|
| Backend | `app/services/elevenlabs_service.py` — MP3 synthesis via ElevenLabs REST |
| Backend | `GET /api/malone/voice/status`, `POST /api/malone/tts` — `app/api/malone_routes.py` |
| Audit | `malone.tts.completed` in `audit_logs` (lengths/duration, no raw text) |
| Frontend | `MaloneAnswerPlayback.jsx` — Speak / Stop / Replay / Auto-read |
| Frontend | `maloneApi.voiceStatus`, `maloneApi.tts` |
| Integration | `ProposalPanel` passes `delivery.answer` into playback |
| Tests | `tests/test_elevenlabs_service.py` |

## Exit criteria

| Criterion | Met |
|-----------|-----|
| Malone can speak grounded answer text | Yes (when env configured) |
| Audio can be stopped | Yes (`Audio.pause` + reset) |
| Audio can be replayed | Yes (cached blob URL) |
| Existing text UI still works | Yes (unchanged answer block) |

## Verification

- `python -m pytest tests -q` — pass  
- `python -m compileall app -q` — pass  
- `npm run build` — pass  

## Deferred

- STT, push-to-talk, request cancellation (Voice Phase 2+).

## References

- `malone_voice_phase1_elevenlabs_execution.md`
- `malone_voice_phase1_playback_plan.md`
- `malone_voice_phase1_config_plan.md`
