# Malone Voice Readiness — Audit Report

**Pass date:** 2026-04-16  
**Scope:** Deterministic audit and planning for hands-free voice (STT, TTS, interaction state, controls, fallbacks) on the **active Malone stack** in `app/` + `src/`. No implementation of the full voice stack in this pass.  
**Active lanes:** `app/`, `src/`, `tracking/`, `tests/` only.

---

## 1. CURRENT MALONE VOICE READINESS

### What already exists that can support voice

- **Stable text Malone round-trip:** `POST /api/malone/chat` accepts `{ "message": string }` and returns a JSON envelope including `delivery.answer` (the user-facing string), plus `truth_packet`, `verification`, and `proposal_record` for governance and audit. This is the correct **single entry** for both typed and spoken user text; voice should remain a **transport layer** on top of it.
- **Authenticated client pattern:** `src/lib/maloneApi.js` sends JSON with `Authorization: Bearer` from `localStorage`, matching how the runtime expects authenticated calls.
- **Answer surface for TTS:** `src/components/malone/ProposalPanel.jsx` renders `response?.delivery?.answer` as the primary visible answer. That string (or the verified delivery string from `verification` when present server-side) is the natural **TTS source** without branching Malone logic.
- **Keyboard-first fallback already present:** `ChatPanel.jsx` provides a textarea, Enter-to-send, loading state, and error display. No change is required to keep “type instead” as the fallback.
- **UI hook for a voice affordance:** `MalonePage.jsx` mounts `VoiceInputButton` in the header. Today it is a **non-functional stub** (label only), but the placement is appropriate for evolving into push-to-talk or “Talk”.
- **Prior design artifacts:** `tracking/04_voice_first_design.md` and `tracking/malone/MALONE_V1_MASTER_PLAN.md` mention voice direction; `tracking/build_map.json` (generated map data) contains references to audio/websocket concepts at the **documentation/map** level, not implemented Malone code paths.
- **Deterministic term inventory:** `tools/malone_voice_inventory.py` plus `tracking/reports/malone_voice_inventory.*` quantify how rarely voice/audio terms appear in active-lane source (see inventory for file-level hits).

### What definitely does not exist yet

- **No microphone capture:** No `MediaRecorder`, `getUserMedia`, or similar in `src/` Malone components (inventory: no `microphone` / `MediaRecorder` matches in Malone UI code).
- **No STT:** No speech-to-text integration, transcript model, or API route for audio upload or streaming transcription in `app/`.
- **No TTS:** No ElevenLabs (or other) integration, no audio bytes endpoint, no client playback of Malone responses.
- **No voice session state:** No React state machine for `idle | listening | processing | speaking`, no shared store for “last spoken text” or audio handle beyond ordinary Malone `useState` for `response`.
- **No streaming Malone responses:** `maloneApi.chat` uses a single `fetch` POST; there is no SSE/WebSocket for partial tokens or streamed audio.
- **No request cancellation for Malone chat:** `ChatPanel` does not pass `AbortSignal` to `fetch`; there is no “stop generating” for the HTTP call. (`cancel` hits in `app/` are for **schedule cancel** APIs, not Malone.)
- **No playback controls:** No `HTMLAudioElement`, Web Audio, or stop/replay UI for Malone output.

**Bottom line:** Malone is **text-complete** for the core assistant loop but **voice-empty** except for a labeled stub button. Legal ingestion and PDF grounding passes did not change Malone chat behavior; they remain separate persistence and retrieval layers until explicitly wired to `truth_packet_service`.

---

## 2. REUSABLE SYSTEM PARTS

### Frontend pieces

| Piece | Role for voice |
|--------|------------------|
| `maloneApi.chat(message)` | Same entry after STT produces `message` string. |
| `ChatPanel` | Transcript can populate the textarea or call `chat` directly; loading/error patterns reusable. |
| `ProposalPanel` / `delivery.answer` | Single string to feed TTS; optional “replay” uses the same field. |
| `MalonePage` | Can hold voice state (listening/speaking), last audio ref, and AbortController for fetch. |
| `VoiceInputButton` | Replace stub with real control wired to PTT or click-to-talk. |

### Backend pieces

| Piece | Role for voice |
|--------|------------------|
| `handle_malone_request` | Unchanged business logic; voice only changes how `message` is obtained. |
| `malone_routes` pattern | New routes (e.g. TTS proxy) can follow the same `Depends(get_current_user)` + JSON/blob patterns as the rest of `app/api`. |
| `openai_service` | Establishes precedent for env-based API keys and timeouts; ElevenLabs config can mirror (separate keys, separate module). |
| Audit / proposal persistence | Continuity of “what Malone said” is already in DB via proposals; voice does not require a second agent path. |

### Service layers

- **Intent, truth packet, render, verify:** Keep as-is; voice does not fork these.
- **Clarification / workflow:** Existing cancellation semantics apply to **workflows and clarifications**, not to HTTP Malone chat; any “cancel response” for voice is a **client-side** abort + audio stop unless you add explicit API support later.

### State / control mechanisms

- **React local state:** Sufficient for V1 (last response text, `Audio` element ref, `AbortController` ref).
- **No WebSocket today:** Real-time streaming is optional and not required for the smallest safe slice.

---

## 3. MISSING VOICE CAPABILITIES

| Capability | Gap |
|-------------|-----|
| **Mic capture** | No `getUserMedia`, no recording pipeline, no permission UX. |
| **STT** | No provider choice wired (browser Web Speech API vs server-side Whisper-class vs vendor STT). |
| **TTS** | No ElevenLabs HTTP client, no audio proxy, no caching policy. |
| **Playback state** | No audio element lifecycle, no “now speaking” sync with text. |
| **Interruption / stop** | No stop for TTS playback; no AbortSignal on `maloneApi.chat`. |
| **Replay / repeat** | No UI to replay last `delivery.answer` audio. |
| **Session continuity** | No explicit “voice turn id” or resume model; proposals give historical continuity but not real-time voice session. |

---

## 4. MINIMUM SAFE VOICE V1

The smallest **production-safe** vertical slice (transport only, same Malone brain):

1. **One “Talk” control** (replace or extend `VoiceInputButton`): start listening or open mic; produce a **transcript string** (STT v1 can be browser API or manual paste for dry runs).
2. **Transcript in text:** Show transcript in the existing message field or a read-only line above it so the user can edit before send.
3. **Submit:** Call existing `maloneApi.chat(transcript)` — no new Malone backend contract.
4. **Malone response:** Use `delivery.answer` (and parity with `verification.delivery_answer` if you standardize on verified text server-side).
5. **ElevenLabs playback:** Frontend requests audio from a **server-side proxy** (recommended) so API keys stay off the browser; play via `Audio` API.
6. **Stop / Replay:** Stop = pause/stop current audio element; Replay = regenerate or replay buffered audio for the **same** answer text (implementation choice: re-fetch TTS vs cache blob in memory for the session).
7. **Fallback:** User can always type in `ChatPanel` and send without voice.

This matches the principle: **voice is a transport/interface layer**, not a parallel Malone agent.

---

## 5. RECOMMENDED IMPLEMENTATION ORDER

Next **10** build actions (after this audit):

1. Add **ElevenLabs server proxy** route in `app/api/` (authenticated) that accepts text + voice settings and returns audio bytes or a short-lived URL; store `ELEVENLABS_API_KEY` server-side only.
2. Add **`maloneApi.speak(text)`** (or `fetchTtsAudio`) in `src/lib/maloneApi.js` calling the proxy; handle errors with user-visible message.
3. Implement **`HTMLAudioElement` (or `new Audio(url)`)** in `MalonePage` or a small `MaloneVoicePlayback` component with **Stop** and **Replay** bound to last answer text.
4. On successful Malone chat response, optionally **auto-play** TTS from `delivery.answer` (feature flag or toggle “Read aloud”).
5. Add **`AbortController`** to `maloneApi.chat` and wire a “Stop request” control in `ChatPanel` / page header to abort in-flight HTTP (best-effort; server may still complete).
6. Replace `VoiceInputButton` stub with **push-to-talk** UI state (`idle` / `listening`) — initially can still use **typed transcript** if STT is not ready.
7. Integrate **STT v1** (prefer smallest scope: **Web Speech API** behind `window.isSecureContext` checks, with clear “not supported” fallback to typing).
8. Pipe STT final transcript into **textarea** or direct `chat()` after user confirms (or auto-send behind a setting).
9. Add **minimal voice interaction state** (listening/speaking/processing) as derived from: mic on, `fetch` loading, `audio` playing.
10. Document **env vars and operational limits** (rate limits, max text length for TTS, PII warning) in `tracking/` and keep `requirements.txt` updated only when new Python deps are added for TTS proxy.

---

## 6. RISKS / BLOCKERS

- **Secrets:** ElevenLabs keys must not ship to the client; a proxy in `app/` is the default-safe pattern.
- **HTTPS / mic:** Browser mic APIs require secure context; local dev must use `https://` or `localhost` consistently with `app/main.py` CORS (`localhost:5173` already allowed).
- **Latency:** Sequential STT → Malone → TTS chains user-perceived delay; acceptable for V1; streaming is not required for first slice.
- **Legal / compliance:** Spoken output of regulated content increases **mis-hearing** risk; keep **text** as source of truth and display `delivery.answer` alongside audio.
- **No server-side “stop Malone”:** Abort only cancels the HTTP client; long-running server work may continue unless you add idempotent job tokens later (out of scope for V1).
- **Inventory noise:** `cancel` matches in `app/api/routes.py` are **schedule** endpoints, not Malone voice — do not confuse with voice interruption.

---

## 7. HARD-FAIL COMPLIANCE CHECK

| Condition | This pass |
|-----------|-----------|
| No passive roots (`backend/`, `frontend/`, `dsos_replacements/`) modified | **Yes** — audit outputs and `tools/` only under allowed roots. |
| No wholesale Malone replacement | **Yes** — `handle_malone_request` and chat contract unchanged. |
| No speculative giant rewrite | **Yes** — plans layer voice as transport over existing chat. |
| Tracking outputs produced | **Yes** — this report, state JSON, plans, next-thread prompt, inventory. |

---

## Appendix: Related reports

- `tracking/reports/malone_voice_architecture_plan.md`
- `tracking/reports/malone_voice_interaction_plan.md`
- `tracking/reports/malone_voice_backend_plan.md`
- `tracking/reports/malone_elevenlabs_plan.md`
- `tracking/reports/malone_stt_plan.md`
- `tracking/reports/malone_voice_inventory.md`
