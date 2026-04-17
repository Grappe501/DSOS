# Malone Voice Phase 2 — Interruption & Control Plan

**Date:** 2026-04-16

## Goals

1. User can **stop** unsafe or unwanted work: in-flight Malone HTTP and in-flight TTS.
2. **Stale** completions never replace newer intent (chat response or spoken answer).
3. Controls stay **explicit** (buttons), with a visible **session** indicator.

## Chat path

| Event | Behavior |
|-------|----------|
| Send while idle | New `AbortController`, increment sequence, `maloneApi.chat(..., { signal })`. |
| Send while loading | Abort prior request; new sequence wins; prior completion ignored. |
| Cancel request | Abort, bump sequence, clear busy; **do not** clear last good Malone response. |
| Response arrives | Apply only if sequence matches latest. |

## TTS path

| Event | Behavior |
|-------|----------|
| New answer (`playbackEpoch` / `playbackKey`) | Abort TTS fetch, pause audio, reset blob, notify `silent`. |
| Speak / Auto-read | Abort any prior TTS fetch; new `AbortController` for MP3. |
| Stop | Abort fetch, pause audio, phase `stopped`. |
| `blob()` or `play()` resolves | Apply only if token and `playbackKey` still match. |

## UI surfaces

- **Cancel request** — `ChatPanel` (only when `loading`).
- **Stop** — `MaloneAnswerPlayback` (when not idle; aborts fetch + playback).
- **Voice session** — header via `VoiceInputButton` (derived state).

## Deferred (Phase 3+)

- Route **STT transcript** through the same table as above (see `tools/malone_voice_stt_handoff.md`).
