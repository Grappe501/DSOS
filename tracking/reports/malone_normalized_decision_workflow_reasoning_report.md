# Malone normalized decision / workflow reasoning — report

## 1. WHY DECISION / WORKFLOW REASONING IS NEEDED

Normalized retrieval surfaces **fields** (requirement level, role, conditions) per chunk or segment, but operational users need **assembled** guidance: ordered steps, who acts, when rules apply, exceptions, and escalation — **without** abandoning citation-first evidence. This pass adds an **augmentation layer** that groups normalized units, builds an auditable action sketch, and appends it **after** raw excerpts, preserving Malone as a single path.

## 2. CURRENT NORMALIZED-RETRIEVAL LIMITATIONS

- Per-item normalized blocks do not **connect** requirements across chunks/segments or source types.
- No first-class **partial workflow** signaling when sources lack explicit step typology.
- **Cross-source** (legal + policy + SOP) was not combined in one decision context for one request.
- **SOP / runbook** content had no dedicated intent + segment bundle parallel to policy.

## 3. TARGET DECISION / WORKFLOW REASONING ARCHITECTURE

- Package `app/services/decision_reasoning/`: context merge from evidence bundles, operational intent routing (keyword heuristics), role/condition/exception/escalation grouping, workflow step ordering (explicit types + facets + safe synthesis), action plan + `source_evidence_map`, JSON serialization, fallback helpers.
- **Truth packet** gains `decision_workflow` plus `packet_meta` audit keys.
- **Deterministic answers** call `format_*_lookup_answer(..., decision_workflow=...)` to append an “Operational guidance” section when safe.

## 4. ROLE / CONDITION / EXCEPTION MODEL

- **Roles**: distinct `applies_to_role` values with referencing `unit_ids`.
- **Conditions / exceptions**: de-duplicated text lists with `unit_id` and `normalized_unit_type` for traceability (no free-form evaluation of user facts).
- **Escalation / reporting**: `escalation_text` and `output_outcome_text` grouped with kind labels.

## 5. LEGAL, POLICY, AND SOP SUPPORT IN THIS PASS

- **legal_handbook**: units from `units_by_chunk_id`; lanes `legal_handbook`; citations via chunk + citation metadata.
- **policy_manual**: `units_by_segment_id`; lane `policy_manual`.
- **sop_workflow**: new segment bundle builder (`build_sop_evidence_bundle_with_normalized`), default version resolver, intent target `sop_workflow` with narrow triggers; same answer formatter path as policy with distinct title line.
- **Cross-source**: optional `MALONE_CROSS_SOURCE_DECISION_ENABLED` + `cross_source_legal_policy_triggered` loads legal + policy bundles together; optional `[sop]` hint pulls SOP segments when cross-source is on.

## 6. FALLBACK / SAFETY MODEL

- Decision layer **disabled** when `MALONE_DECISION_REASONING_ENABLED` resolves false (default: follows normalized retrieval gate).
- **No merged normalized units** → `fallback_reason` on `decision_workflow`; formatter skips structured operational section (`should_emit_structured_sections`).
- **Partial workflows** flagged with `partial_workflow` + reason; answer includes explicit caveat lines.
- **Low-trust dominance** (`caution_low_trust_dominant`) adds a caution line; does not strip citation-first body.
- **Guardrails**: `decision_workflow_supplementary_forbidden_claims` appended when structured sections emit.

## 7. WHAT THIS PASS IMPLEMENTED

- `app/services/decision_reasoning/*` modules (context, workflow assembly, routing, roles, conditions, exceptions, escalations, action plan, fallback, serialization).
- `build_decision_workflow_block` API; truth packet enrichment; SOP bundle + intent; cross-source bundle wiring in `malone_service`.
- `answer_formatter` operational appendix; `guardrails` supplementary rules; `serialization` exposes `structured_facets` for facet-aware ordering.
- `tools/debug_decision_reasoning.py`; `tests/test_decision_reasoning.py`.
- Tracking reports (this suite).

## 8. WHAT REMAINS DEFERRED

- LLM render path (`render_conversational_response`) does not yet consume `decision_workflow` structurally (deterministic paths upgraded first).
- Embedding-based re-ranking of merged units across sources.
- Richer SOP-specific parsers / step extraction beyond normalized unit types + facets.
- UI panels for decision/workflow visualization in `src/` (not required for this pass).

## 9. HARD-FAIL COMPLIANCE CHECK

- **Did not modify** `backend/`, `frontend/`, or `dsos_replacements/`.
- **Did not** replace citation-first legal behavior; operational text is **append-only**.
- **Did not** invent a second agent or parallel Malone stack.
- **Fallbacks** implemented for empty decision context and low-trust warnings.
- **Tracking outputs** produced (this report + state JSON + companion notes).
