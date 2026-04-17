# Malone normalized retrieval + answer upgrade — report

## 1. WHY NORMALIZED RETRIEVAL IS NEEDED

Lexical and citation retrieval return **raw chunks** with strong grounding but weak **semantic structure** for users: obligation strength, roles, exceptions, and escalation are buried in prose. Normalized knowledge units (already produced above ingestion) capture those dimensions deterministically. Surfacing them **after** citations and excerpts makes answers sharper without abandoning evidence-first discipline.

## 2. CURRENT RAW-EVIDENCE LIMITATIONS

- Answers listed citations and snippets but not **requirement level**, **exceptions**, or **escalation** unless the model paraphrased raw text.
- Policy segments had no first-class path in Malone intent/delivery parallel to legal.
- Truth packets lacked explicit **normalized unit counts** for audit.

## 3. TARGET NORMALIZED RETRIEVAL ARCHITECTURE

- New package `app/services/normalized_retrieval/`: legal and policy selectors, bundle attachment, ranking, fallback, serialization.
- Legal bundle: after chunk retrieval, attach `normalized.units_by_chunk_id` scoped to `legal_source_version_id` and successful normalization runs.
- Policy bundle: segment keyword search, then attach `normalized.units_by_segment_id`.
- Single Malone request path: `handle_malone_request` unchanged in structure; evidence enrichment is additive.

## 4. ANSWER UPGRADE STRATEGY

- `format_legal_lookup_answer` and `format_policy_lookup_answer` accept optional `normalized_bundle`.
- Output order: **disclaimer → (heuristic banner if normalized) → per item: primary grounding (citation/segment) → excerpt → up to two normalized blocks**.
- Normalized blocks include type, requirement level, role, action, summary, condition/exception/escalation (truncated), confidence/review metadata.

## 5. LEGAL AND POLICY SUPPORT IN THIS PASS

- **legal_handbook**: `build_legal_evidence_bundle` calls `attach_normalized_to_legal_bundle` when `MALONE_NORMALIZED_RETRIEVAL_ENABLED` (default: follow `MALONE_LEGAL_EVIDENCE_ENABLED`). Deterministic delivery passes `normalized` into the formatter.
- **policy_manual**: New intent trigger + `build_policy_evidence_bundle` + `enrich_truth_packet_with_policy` + `_deliver_policy_manual_deterministic` when `MALONE_POLICY_EVIDENCE_ENABLED` / `MALONE_POLICY_LOOKUP_ENABLED`.

## 6. FALLBACK / SAFETY MODEL

- Rejected/superseded units excluded; unknown confidence and draft review may still display with explicit caveat.
- Missing normalized data → raw-only answer; `fallback_reason` on bundle for logs.
- Truth packet web search suppressed for `policy_manual` like `legal_handbook`.
- See `malone_normalized_retrieval_fallbacks.md`.

## 7. WHAT THIS PASS IMPLEMENTED

- `app/services/normalized_retrieval/` (bundle builder, legal/policy selectors, ranking, fallback, serialization, `__init__`).
- `legal_evidence_service`: env gates, `build_policy_evidence_bundle`, `enrich_truth_packet_with_policy`, legal bundle auto-attach.
- `malone_service`: policy evidence build, truth enrichment, policy deterministic delivery.
- `answer_formatter`: legal + policy structured sections.
- `intent_service`: `policy_manual` target; `truth_packet_service`: web/clarification rules for policy.
- `tools/debug_normalized_retrieval.py`; `tests/test_normalized_retrieval.py`.

## 8. WHAT REMAINS DEFERRED

- LLM render path (`_deliver_rendered_response`) does not yet inject normalized blocks into OpenAI prompts (deterministic paths only in this pass).
- Embedding re-ranking of normalized units.
- API routes dedicated to browsing normalized inventory.
- Automatic selection among multiple normalization runs per version (currently: any passing run’s units).

## 9. HARD-FAIL COMPLIANCE CHECK

- **Did not modify** `backend/`, `frontend/`, or `dsos_replacements/`.
- **Did not** replace citation-first legal behavior or remove deterministic legal delivery.
- **Raw evidence** remains mandatory in formatted output before normalized addenda.
- **Fallbacks** implemented and documented.
- **Tracking outputs** produced (this report suite + state JSON).
