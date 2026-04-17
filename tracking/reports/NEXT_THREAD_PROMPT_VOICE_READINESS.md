# Next Thread — Malone Voice Readiness (post-audit)

You are continuing DSOS / Malone after the **voice readiness audit** (2026-04-16).

## Completed this pass

- Audited active-lane Malone stack (`app/`, `src/`) for voice/STT/TTS readiness.
- Produced:
  - `tracking/reports/malone_voice_readiness_report.md`
  - `tracking/reports/malone_voice_readiness_state.json`
  - `tracking/reports/malone_voice_architecture_plan.md`
  - `tracking/reports/malone_voice_interaction_plan.md`
  - `tracking/reports/malone_voice_backend_plan.md`
  - `tracking/reports/malone_elevenlabs_plan.md`
  - `tracking/reports/malone_stt_plan.md`
  - `tracking/reports/malone_voice_inventory.json` / `.md` (from `tools/malone_voice_inventory.py`)

## Findings snapshot

- Malone chat is **text-only** end-to-end: `POST /api/malone/chat` → `handle_malone_request` → `delivery.answer` shown in `ProposalPanel`.
- **Voice UI is a stub:** `src/components/malone/VoiceInputButton.jsx` — no mic, STT, TTS, or playback.
- **No** WebSocket Malone streaming; **no** `AbortSignal` on chat `fetch` today.
- ElevenLabs and STT are **planned**, not implemented.

## Active lanes (typical)

`app/`, `src/`, `tracking/`, `tests/` — do **not** edit passive roots `backend/`, `frontend/`, `dsos_replacements/` unless a future pass explicitly expands scope.

## Suggested implementation order (first slice)

1. Server-side **ElevenLabs TTS proxy** + env config.
2. Client **audio playback** + **Stop** / **Replay** for `delivery.answer`.
3. Optional **auto-read** toggle.
4. **AbortController** on `maloneApi.chat` for “stop request.”
5. Replace `VoiceInputButton` with real **push-to-talk** or **Talk** flow.
6. **STT v1** (Web Speech API or server upload per `malone_stt_plan.md`).
7. Voice **state** flags: listening / processing / speaking.

## Hard-fail conditions

- Treating voice as a **second Malone agent** instead of transport on the same chat path.
- Shipping **ElevenLabs API keys** to the browser.
- Skipping **text fallback** for governed answers.
- Wholesale replacement of `handle_malone_request` for voice.

## Read first

- `tracking/reports/malone_voice_readiness_report.md`
- `app/api/malone_routes.py`
- `src/lib/maloneApi.js`
- `src/pages/MalonePage.jsx`
- `src/components/malone/ChatPanel.jsx`
- `src/components/malone/ProposalPanel.jsx`
