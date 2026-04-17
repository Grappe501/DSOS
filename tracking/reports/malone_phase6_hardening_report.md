# Malone Phase 6 — Production Hardening of Legal Agent Slice

**Status:** Complete  
**Date:** 2026-04-16

## Hardening measures

| Area | Implementation |
|------|------------------|
| Empty evidence | Formatter returns explicit “no matching excerpts” guidance; bundle includes `warnings`. |
| Web bleed | `legal_handbook` intent disables `retrieval_rules.allow_web_search`. |
| Clarification noise | Legal intent bypasses generic clarification-for-general-requests path. |
| Duplicate hits | Retrieval dedupe by chunk id across lexical and citation hydration. |
| Audit | `LegalAnswerTrace` + `log_malone_action` for delivery path. |
| Regression tests | `tests/test_legal_malone_integration.py` — formatter, env gating, in-memory scoped retrieval. |

## Known gaps (explicit)

- Embeddings / vector retrieval not enabled (hybrid stub).
- Intent triggers are **keyword-based**; ambiguous queries may miss `legal_handbook` classification unless they match needles.
- OpenAI path with legal evidence in packet (lookup **off**) does not automatically inject citations into LLM prompts—bundle is inspectable in API responses for clients that read `truth_packet`.

## Operational notes

- Enable flags only in environments with **trusted ingested** handbook data.
- Re-ingest produces new `legal_source_version_id`; retrieval defaults to latest version.

## Verification

See `malone_phase6_hardening_state.json`.
