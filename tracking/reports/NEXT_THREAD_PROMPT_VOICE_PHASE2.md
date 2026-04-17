# Next thread — Malone Voice Phase 3 (STT / listen)

**Prereq:** Phase 2 complete (`malone_voice_phase2_control_report.md`). One Malone spine; keyboard remains primary until STT ships.

## Mission

Implement **speech-to-text as input transport** into the **existing** `maloneApi.chat` flow, reusing **AbortController** and stale guards from `ChatPanel`. Do **not** fork Malone or add a parallel voice backend.

## Read first

- `tracking/reports/malone_voice_phase2_control_report.md`
- `tracking/reports/malone_voice_phase2_interruption_plan.md`
- `tools/malone_voice_stt_handoff.md`
- `src/lib/maloneVoiceSession.js` (`STT_HANDOFF_CONTRACT`)
- `src/components/malone/ChatPanel.jsx`
- `src/components/malone/VoiceInputButton.jsx`

## Build (Phase 3 scope)

1. **Explicit user gesture** before any microphone access (no always-on wake in this pass unless product mandates and control is proven).
2. **Transcript →** same submit path as typed chat (`maloneApi.chat(text, { signal })`), shared abort policy.
3. **Barge-in (optional but valuable):** starting listen or new STT session aborts TTS via existing playback abort hooks.
4. **UI:** Enable or replace **Mic (STT — later)** with real control; keep **Listen** semantics aligned with listen-mode toggle.
5. **Tests / validation:** `python -m pytest tests -q`, `python -m compileall app -q`, `npm run build`; add tracking reports for Phase 3.

## Hard constraints

- Active lane only: `app/`, `src/`, `tracking/`, `tests/`, `tools/`.
- Do **not** modify `backend/`, `frontend/`, `dsos_replacements/` unless a future phase explicitly allows.
- Do **not** weaken legal grounding, citations, or evidence behavior.

## Deliverables

- `tracking/reports/malone_voice_phase3_stt_report.md` (or equivalent naming)
- `tracking/reports/malone_voice_phase3_stt_state.json`
- `tracking/reports/NEXT_THREAD_PROMPT_VOICE_PHASE3.md`
