# Malone Voice Phase 3 — Listen / transcript UX notes

**Date:** 2026-04-16

## Principles

1. **Keyboard and mouse stay primary.** Voice is additive; never block typing.
2. **No silent failure.** Unsupported browser, denied mic, or recognition errors surface short, actionable copy.
3. **Review before send.** User always sees and can edit text before it becomes a Malone request.

## Control mapping

| Control | Behavior |
|---------|----------|
| **Listen** | Starts Web Speech capture after optional mic preflight; triggers TTS stop (barge-in) when playback is active. |
| **Stop listening** | Ends capture and opens review with combined transcript. |
| **Cancel listen** | Discards capture without sending. |
| **Send transcript** | Submits via the same Malone chat path as **Send** on the main form. |
| **Cancel** (review) | Clears draft and exits voice flow. |

## Trust copy (recommended placement)

- Browsers may process speech in the cloud; users in regulated contexts should prefer typing when required by policy.
- Malone’s legal grounding does not change because input was spoken — operators should still read the on-screen answer.

## Session label

Header **Voice session** reflects coarse state (for example Listening, Transcribing, Review transcript) so users can tell what the page is doing without relying on audio alone.
