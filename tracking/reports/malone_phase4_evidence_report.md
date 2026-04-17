# Malone Phase 4 — Legal Evidence Integration into Malone

**Status:** Complete  
**Date:** 2026-04-16

## Summary

Grounded legal evidence is attached to Malone’s **truth packet** on the existing request path—no second agent, no replacement of the proposal/workflow loop.

## Integration points

| Component | Behavior |
|-----------|----------|
| `intent_service.classify_intent` | When `MALONE_LEGAL_EVIDENCE_ENABLED` and narrow Arkansas/ASBP triggers → `target: legal_handbook`, `legal_profile: arkansas_asbp_handbook`. |
| `legal_evidence_service.build_legal_evidence_bundle` | Citation-first then lexical; scoped to latest `legal_source_version_id` (or explicit). |
| `legal_evidence_service.enrich_truth_packet_with_legal` | Adds `legal_evidence`, extends `allowed_claims` / `forbidden_claims`. |
| `truth_packet_service` | Blocks web search for `legal_handbook`; skips clarification nag for legal path. |
| `malone_service.handle_malone_request` | Builds bundle, enriches packet, persists `legal_answer_traces` (flush with session). |

## Feature flag

- **`MALONE_LEGAL_EVIDENCE_ENABLED`** — must be set for legal intent classification and bundle attachment.

## Fallback

- Non-legal behavior unchanged when flag is unset.
- With flag set but empty DB, bundle carries warnings (`no_legal_source_version_in_database`, `no_lexical_or_citation_hits`).

## Verification

See `malone_phase4_evidence_state.json`.
