# Malone business operating copilot — pass report

## 1. WHY A BUSINESS OPERATING COPILOT LAYER IS NEEDED

Operational teams ask scenario questions (“what next,” “who owns this,” “when to escalate”) that are not fully answered by citation lists or single-pattern layouts alone. The business operating copilot sits on the same Malone path, after retrieval, normalization, smart patterns, and decision/workflow assembly, to turn **source-grounded** evidence into **structured operational guidance** without replacing citations or inventing obligations.

## 2. CURRENT SMART-ANSWER LIMITATIONS

Smart answer patterns improve layout and intent alignment (requirement, workflow, exception, source locator) but do not, by themselves, maintain a consistent cross-source operational frame (required vs recommended vs uncertain vs escalate) or a single inspectable scenario route. Decision/workflow reasoning adds steps and roles from normalized units; the copilot layer adds **scenario focus**, **uncertainty surfacing**, and **explicit supporting-source mix** in one additive block.

## 3. TARGET OPERATING COPILOT ARCHITECTURE

One Malone path only. Flow: evidence bundles → `build_decision_workflow_block` → `build_operating_copilot_block` → `enrich_truth_packet_with_operating_copilot` → formatters / pattern integration append text via `append_operating_copilot_lines`. The copilot never replaces the legal/policy/SOP body; it appends after decision/workflow sections when emission rules allow.

## 4. SCENARIO ROUTING STRATEGY

Deterministic `route_scenario` scores user-message phrases (next steps, role, exception, escalation, operating summary) with an explicit tie-break order (escalation → exception → role → next steps → operating summary). `decision_workflow` may weakly boost escalation or next-step focus. Operational queries are gated by `is_operational_copilot_query` (scenario scores or operational/workflow/compliance vocabulary).

## 5. ROLE / ESCALATION / EXCEPTION MODEL

Roles, conditions, exceptions, and escalations are drawn from the merged decision/workflow structure (`build_action_plan` outputs) when present. The copilot distinguishes **required vs recommended vs uncertain vs escalate** in a fixed “distinction” object that reminds users to verify excerpts and normalized fields. Missing owners or partial workflows increase uncertainty and may trigger minimal safe emission.

## 6. LEGAL, POLICY, AND SOP SUPPORT IN THIS PASS

- **legal_handbook**: Citation-first behavior unchanged; copilot appends only when enabled and evidence scope has items; formatter keeps citations in the main body.
- **policy_manual**: Same path via policy bundles and segment-normalized units; responsibility and step hints flow through decision/workflow into copilot lines.
- **sop_workflow**: Included in merge, scope counts, and context when SOP bundles are loaded; participation depth follows the same normalized-unit and bundle availability as decision reasoning.

## 7. FALLBACK / SAFETY MODEL

If copilot is disabled, the query is not operational, or there are no evidence items, the block is disabled with a reason. If evidence exists but normalized guidance is too thin, a **minimal** block may emit uncertainty notes only (`emit_minimal_only`). If `fallback_reason` is set on a non-minimal block, the section is suppressed by `should_emit_operating_copilot_section` to avoid fabricated runbooks. Truth packet gains supplementary forbidden claims when structured copilot guidance is attached.

## 8. WHAT THIS PASS IMPLEMENTED

- Package `app/services/operating_copilot/` (scenario router, context, merge summary, guidance builders, uncertainty, serialization, fallback).
- Wiring in `malone_service.py`, enrichment in `legal_evidence_service.py`, append in `answer_formatter.py` and `answer_patterns/integration.py`, guardrails in `guardrails.py`.
- Tests in `tests/test_operating_copilot.py` and debug helper `tools/debug_operating_copilot.py`.
- This report set under `tracking/reports/`.

## 9. WHAT REMAINS DEFERRED

- Richer NLP-free extraction of role labels from free text beyond normalized fields.
- Deeper SOP-specific checkpoint modeling when segment metadata is sparse.
- UI-specific copilot panels (out of scope for this pass; text appendix only).
- Cross-session memory of operational state.

## 10. HARD-FAIL COMPLIANCE CHECK

- **Single path**: No second agent; copilot is an enrichment on the existing pipeline.
- **Citations / legal**: Legal answers remain citation-first; copilot does not remove excerpts.
- **No unsupported certainty**: Distinction and uncertainty blocks are always present when full guidance emits; minimal path explicitly says guidance is thin.
- **Fallbacks**: Disabled, non-operational, no items, or fallback_reason (non-minimal) prevent misleading sections.
- **Scope**: Changes confined to `app/`, `tests/`, `tools/`, `tracking/` as required for this pass.
