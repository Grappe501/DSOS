# Malone Voice — Backend Integration Plan

**Date:** 2026-04-16  
**Scope:** `app/` only (FastAPI services under active lane). **Do not** modify `backend/`, `frontend/`, `dsos_replacements/`.

---

## What exists today

- **`POST /api/malone/chat`** — `app/api/malone_routes.py` — body: `MaloneChatRequest { message: str }` → `handle_malone_request`. No audio, no streaming.
- **Auth** — `Depends(get_current_user)` on Malone routes; TTS/STT routes should use the same pattern.
- **Dependencies** — `requirements.txt` lists FastAPI stack + `pypdf`; no ElevenLabs SDK required if using `httpx` or `urllib` (match `openai_service` style).

---

## Recommended backend additions (phased)

### Phase A — TTS proxy (highest priority)

- **Route:** e.g. `POST /api/malone/tts` or `POST /api/voice/tts` with JSON `{ "text": "...", "voice_id": "optional" }`.
- **Behavior:** Validate length (align with `OPENAI_MAX_RENDER_CHARS` order-of-magnitude), call ElevenLabs, return `audio/mpeg` or `audio/pcm` with correct `Content-Type`.
- **Security:** API key from environment only; rate-limit per user id if needed (future middleware).
- **Logging:** Audit log entry for `malone.tts.requested` with duration, byte size, **no** raw audio in logs.

### Phase B — STT (optional server path)

- If browser STT is insufficient, add `POST /api/voice/stt` with `multipart/form-data` audio upload.
- Requires **size limits**, **content-type checks**, and explicit **virus/storage policy** (prefer no persistence for V1).

### Phase C — Cancellation

- HTTP **AbortSignal** is client-side; server cannot rely on it for strong cancellation without request-scoped work units.
- For V1, document that “stop” stops **playback** and **client fetch**; server-side LLM/render may complete.

---

## Malone core: no changes required for V1 voice

- `handle_malone_request` remains the single brain; voice sends **strings** only.

---

## CORS

- `app/main.py` allows `localhost:5173`; ensure any new fetch from the Vite app uses same origin or listed origins.

---

## Testing hooks

- Unit tests in `tests/` for text length validation and ElevenLabs error mapping (mock HTTP).
- No integration test against real ElevenLabs in CI without secrets.

---

## Draft config checklist

| Variable | Purpose |
|----------|---------|
| `ELEVENLABS_API_KEY` | Server-side TTS auth |
| `ELEVENLABS_VOICE_ID` | Default voice |
| `ELEVENLABS_TTS_TIMEOUT_SECONDS` | Bound latency |
| `MALONE_TTS_MAX_CHARS` | Align with safe playback length |
