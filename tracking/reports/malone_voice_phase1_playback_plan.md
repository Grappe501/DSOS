# Voice Phase 1 — Frontend Playback Plan

## Principle

Playback consumes **exactly** the string already rendered for the user: `response.delivery.answer` in `ProposalPanel` → `MaloneAnswerPlayback` via `answerText`.

No parallel “voice answer” object. Legal citations and truth packet payloads are unchanged; audio is a rendering of the same text.

## Component

**`src/components/malone/MaloneAnswerPlayback.jsx`**

| Control | Behavior |
|---------|----------|
| **Speak answer** | `POST /api/malone/tts` with full answer text; plays returned MP3 via `Audio()` + blob URL. |
| **Stop** | Pause and reset `currentTime` (does not cancel in-flight HTTP in V1; see Voice Phase 2). |
| **Replay** | Re-play cached blob from start (no refetch if cache key unchanged). |
| **Auto-read** | When enabled, plays once per new `playbackKey` (proposal id preferred, else answer string). Preference stored in `localStorage` key `malone_tts_auto_read`. |

## API client

**`src/lib/maloneApi.js`**

- `voiceStatus()` — probes `GET /api/malone/voice/status`.
- `tts(text, { signal })` — optional `AbortSignal` reserved for Voice Phase 2.

## UX

- If TTS is not configured, UI shows “TTS unavailable” and disables controls (status check).
- Text layout, `pre-wrap` answer block, and technical details are unchanged.

## Vite

- Dev server proxies `/api` to FastAPI (`vite.config.js`); no CORS changes required for same-origin `/api` calls.
