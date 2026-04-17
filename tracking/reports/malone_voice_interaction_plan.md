# Malone Voice — UI / UX Interaction Plan

**Date:** 2026-04-16  
**Goal:** Hands-free as **primary mode** eventually; **keyboard and mouse** always available. No speculative UX chrome beyond what supports safety and clarity.

---

## Current UI facts

- **Malone page:** `src/pages/MalonePage.jsx` — header includes `VoiceInputButton` (stub), body stacks `ChatPanel` then `ProposalPanel`.
- **Input:** `ChatPanel` — textarea, Send, Enter vs Shift+Enter documented in helper text.
- **Output:** `ProposalPanel` — `delivery.answer` first; technical JSON behind `<details>`.

---

## V1 interaction model (smallest safe)

| User action | System behavior |
|-------------|-----------------|
| **Talk** | Request mic permission if using browser capture; show **listening** state; show **transcript** in text before send (editable). |
| **Send / confirm** | Same as today: POST chat with final string. |
| **Read aloud** | After response, play TTS of `delivery.answer` (toggle or automatic once). |
| **Stop** | Stop audio playback immediately; optionally abort in-flight HTTP if a request is still running. |
| **Replay** | Re-request TTS for the same answer text or replay buffered audio. |
| **Type instead** | User uses textarea — no mode switch required; voice controls disabled or idle. |

---

## Control placement

- **Header:** Keep primary voice affordance near `VoiceInputButton` (Talk / Listen).
- **Answer card:** Add **Stop** and **Replay** next to “Malone Output” when audio is available or last answer exists.
- **Chat card:** Optional **“Use transcript”** / **Edit before send** — reduces error from misrecognition.

---

## States (minimal)

1. **Idle** — mic off, no audio playing, no in-flight request.
2. **Listening** — mic on or STT session active.
3. **Processing** — `maloneApi.chat` in flight (`loading` true).
4. **Speaking** — TTS audio playing.

Derived flags avoid a heavy state machine library for V1.

---

## Accessibility and safety

- Always show **the same answer text** that is spoken; audio is supplementary.
- Visible **error** when mic denied, STT fails, or TTS fails — fall back to text silently reading is not enough for compliance-sensitive content.
- Do not hide **approval / blocked** states behind audio only; `delivery.mode` must remain inspectable in text.

---

## What we are not building in V1

- Wake word, always-on listening, or voice shortcuts.
- Streaming partial TTS while Malone is still generating text.
- Separate “voice conversation history” UI — use existing proposal list and details.
