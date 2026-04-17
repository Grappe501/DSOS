# Next thread — Malone Voice Phase 4 (post–STT hardening)

**Prereq:** Phase 3 complete (`malone_voice_phase3_stt_report.md`). One Malone spine; typed input remains fully supported.

## Mission

Harden **browser STT** and voice UX for production: language/locale selection, clearer recovery from `no-speech` / network errors, optional **server-side STT** only if browser STT is insufficient for policy or quality. Do **not** fork Malone reasoning.

## Read first

- `tracking/reports/malone_voice_phase3_stt_report.md`
- `tracking/reports/malone_voice_phase3_browser_stt_plan.md`
- `src/hooks/useMaloneChatRequest.js`
- `src/components/malone/VoiceInputButton.jsx`

## Build (Phase 4 scope)

1. Telemetry or structured logging (client-side dev logs first) for STT start/stop/error counts.
2. Optional **locale** prop or user setting wired to `createSpeechRecognition({ lang })`.
3. Evaluate **server STT** only with explicit security review — still output plain text into `maloneApi.chat`.
4. Hands-free **activation** only after STT reliability is proven (no default always-on wake).

## Hard constraints

- Active lane only: `app/`, `src/`, `tracking/`, `tests/`, `tools/`.
- Do **not** modify `backend/`, `frontend/`, `dsos_replacements/` unless a future phase explicitly allows.
- Do **not** add a parallel Malone chat route for voice.

## Deliverables

- Phase 4 tracking report + state JSON + next-thread prompt under `tracking/reports/`.
