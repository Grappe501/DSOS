# Voice Phase 1 — Security & Configuration Plan

## Secrets

- **`ELEVENLABS_API_KEY`** — Set only on the **application server** or secret manager. Never commit; never embed in `src/`.
- The browser only receives **MP3 bytes** and **JSON error messages** from authenticated routes.

## Auth

- `GET /api/malone/voice/status` and `POST /api/malone/tts` use **`Depends(get_current_user)`** — same session as Malone chat.

## Abuse / cost controls

- **`MALONE_TTS_MAX_CHARS`** (default `2000`) — enforced in `elevenlabs_service.synthesize_speech_mp3`.
- **`MALONE_TTS_ENABLED`** — global off switch without code deploy if set to `false`/`0`.

## Logging & audit

- TTS completion writes **`malone.tts.completed`** to `audit_logs` with `text_length`, `audio_bytes`, `duration_ms` — **not** full user text.
- Application log on ElevenLabs HTTP errors truncates detail (~200 chars).

## Operational checklist

1. Create ElevenLabs account and API key; pick a **voice id** from the ElevenLabs UI.
2. Set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` in the runtime environment.
3. Optionally tune `ELEVENLABS_MODEL_ID` and timeouts.
4. Confirm organizational approval for processing regulated content through ElevenLabs (see `malone_elevenlabs_plan.md`).

## Local development

- Without keys, `/api/malone/voice/status` reports `tts_configured: false`; UI disables playback but Malone chat remains fully usable.
