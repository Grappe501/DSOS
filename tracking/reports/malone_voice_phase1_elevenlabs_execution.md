# Voice Phase 1 — ElevenLabs Execution Note

**Module:** `app/services/elevenlabs_service.py`  
**Transport:** `urllib.request` (same style as `openai_service`; no extra pip dependency).

## Endpoint

- `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
- Headers: `xi-api-key`, `Content-Type: application/json`, `Accept: audio/mpeg`
- Body: `{ "text": "<trimmed>", "model_id": "<ELEVENLABS_MODEL_ID>" }`
- Response: raw MP3 bytes.

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `ELEVENLABS_API_KEY` | Yes | Server-only API key |
| `ELEVENLABS_VOICE_ID` | Yes | Default voice id |
| `ELEVENLABS_MODEL_ID` | No (default `eleven_multilingual_v2`) | TTS model |
| `ELEVENLABS_TTS_TIMEOUT_SECONDS` | No (default `60`) | HTTP timeout |
| `MALONE_TTS_ENABLED` | No (default on) | Kill switch |
| `MALONE_TTS_MAX_CHARS` | No (default `2000`) | Abuse / cost guard |

## FastAPI surface

- **`POST /api/malone/tts`** — JSON `{ "text": string, "voice_id": optional }`; returns `audio/mpeg` with `Cache-Control: no-store`.
- **`GET /api/malone/voice/status`** — `{ tts_configured, max_chars, tts_enabled_flag }` for UI gating (no secrets).

## Errors

- `ElevenLabsTTSError` → HTTP 400 for validation/provider errors after configuration check.
- Missing configuration → HTTP 503 before calling ElevenLabs.

## Tests

- `tests/test_elevenlabs_service.py` — mocks `urlopen`; no live API calls in CI.
