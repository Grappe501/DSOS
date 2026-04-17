# Malone Voice — ElevenLabs Integration Plan

**Date:** 2026-04-16  
**Role:** Initial **text-to-speech** provider for Malone spoken output. STT is out of scope here (see `malone_stt_plan.md`).

---

## Why ElevenLabs first

- Product choice for natural playback quality.
- Fits **server-side proxy** pattern: keep keys off the SPA in `src/`.

---

## Integration shape (recommended)

1. **Server-only API key** — `ELEVENLABS_API_KEY` read in `app/services/elevenlabs_service.py` (or similar).
2. **HTTP** — Use ElevenLabs REST “text to speech” endpoint with `httpx` or `urllib.request` (consistent with `openai_service` patterns).
3. **Proxy route** — Authenticated FastAPI route returns binary audio to the browser; `fetch` uses `arrayBuffer()` and `Blob` URL for `Audio` playback.
4. **Text source** — Prefer `delivery.answer` text returned from `handle_malone_request`; optionally normalize whitespace only (avoid stripping legal citations).

---

## Request/response concerns

- **Max length:** Cap text length server-side to prevent abuse; align with Malone answer limits (~2k chars context already exists in OpenAI path).
- **Voice selection:** Default voice from env; optional override for admin-only later.
- **Errors:** Map HTTP 401/429 to clear JSON errors for the UI (“TTS unavailable”).

---

## Security

- Never expose API key to `src/`.
- Do not log full user text in production if policy forbids; log hashes or lengths only.

---

## Operational

- Monitor latency and 429 rate limits; queue or backoff in a later phase.
- **No** requirement to add ElevenLabs to `requirements.txt` until implementation chooses `httpx` vs stdlib; if `httpx` is added, pin version in `requirements.txt` when implemented.

---

## Compliance note

- ElevenLabs processing of pharmacy/legal content may have **vendor terms** implications; confirm organizational approval before production enablement.
