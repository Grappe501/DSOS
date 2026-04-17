# Next Thread — Voice Kickoff Complete → Voice Phase 2

## Completed (this thread)

- Voice Phase **1** (TTS foundation): server ElevenLabs proxy, playback controls, auto-read toggle, tests, build green.
- Artifacts: `malone_voice_kickoff_report.md`, `malone_voice_kickoff_state.json`, phase-1 execution/plan notes, `NEXT_THREAD_PROMPT_VOICE_PHASE1.md`.

## Hard rules

- One Malone spine: STT (later) submits **text** to existing `/api/malone/chat`; TTS reads **`delivery.answer`** only.
- Do not modify `backend/`, `frontend/`, `dsos_replacements/`.

## Next: Voice Phase 2 — Interruption / control

1. **`AbortController`** on `maloneApi.chat` and `maloneApi.tts` (wire `signal` through `ChatPanel` / playback).
2. Stop in-flight TTS fetch when user hits Stop or sends a new message.
3. Prevent overlapping playback and stale answer audio (session / response id guards).
4. Explicit UI states: `speaking` / `idle` / `loading` (refine `MaloneAnswerPlayback`).

## Boot

- Read `tracking/reports/malone_voice_phase1_tts_report.md`
- Set env vars per `malone_voice_phase1_config_plan.md` to test TTS locally.
