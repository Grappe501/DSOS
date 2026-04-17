# Malone scenario memory + decision trace — pass report

## 1. WHY SCENARIO MEMORY + DECISION TRACE IS NEEDED

Operational and compliance teams need **repeatable audit trails** of how Malone combined evidence, normalized units, answer patterns, and decision/workflow reasoning for a given question. Without persisted scenario snapshots, prior turns cannot be compared fairly to new evidence, and consistency review is limited to ephemeral responses.

## 2. CURRENT DECISION-REASONING LIMITATIONS

Decision/workflow reasoning enriches the **current** truth packet but does not retain a durable, queryable record of the assembled `decision_workflow` block, `source_evidence_map`, or answer-pattern selection across sessions. Legal answer traces cover handbook chunks only; they do not capture the full cross-source operational picture.

## 3. TARGET SCENARIO MEMORY ARCHITECTURE

`MaloneScenarioMemory` rows anchor a **proposal-scoped** situation: normalized prompt fingerprint, scenario type (`intent_target|primary_route`), source types present, source-version snapshot JSON, delivery mode/status, and review/audit status. One Malone path: records are written after delivery when eligibility and feature flags allow. Prior scenarios are **optional context** on the truth packet (`scenario_memory_context`), never a parallel agent.

## 4. TARGET DECISION TRACE ARCHITECTURE

`MaloneDecisionTrace` rows (1:1 with scenario memory) store JSON snapshots: answer pattern trace, serialized `decision_workflow`, `source_evidence_map`, normalized unit id references, fallback flags, `packet_meta` snapshot, optional operating-copilot snapshot, and verification snapshot. Serialization is size-bounded in `trace_serialization.dumps_limited` to keep rows inspectable without unbounded blobs.

## 5. SCENARIO COMPARISON STRATEGY

`find_prior_scenario_analogs` scores recent **active** memories by fingerprint match and token overlap, with intent-target weighting and source-version drift warnings via `should_suppress_prior_due_to_conflict`. `compare_to_prior_row` returns a structured diff (patterns, routes, source-type overlap, weak-match flag). Nothing in this layer asserts “same scenario.”

## 6. MEMORY SAFETY / PRECEDENCE MODEL

`PRECEDENCE_NOTE` and `current_evidence_outranks_memory()` document the invariant: **current retrieval and citations always win.** Prior rows may inform review only. Optional `MALONE_SCENARIO_MEMORY_APPEND` controls whether priors surface in formatted answers; default keeps citation-first bodies unchanged. Supplementary forbidden claims apply when priors attach.

## 7. WHAT THIS PASS IMPLEMENTED

- ORM models and Alembic `0007` migration + `schemas/scenario_memory_decision_trace_v0.sql`.
- Package `app/services/scenario_memory/` (store, retrieval, comparator, classifier, evidence linking, precedence, trace serialization, fallback).
- Malone integration: optional prior context before delivery; persist trace after proposal save with `db.commit()`.
- Guardrails for prior context; `tools/debug_scenario_memory.py`; tests in `tests/test_scenario_memory.py`.

## 8. WHAT REMAINS DEFERRED

- Vector / embedding similarity and cross-tenant isolation policies.
- UI for browsing scenario memory and approving `review_audit_status`.
- Automated archival rules for `memory_status`.
- Persisted “comparison event” rows if product needs immutable comparison audit logs.

## 9. HARD-FAIL COMPLIANCE CHECK

- **Single path**: No memory-first bypass; persistence runs inside `handle_malone_request` only.
- **Evidence primacy**: Precedence helpers and disclaimers; priors secondary.
- **Legal determinism**: No change to citation-first formatters unless explicit append env is set.
- **Scope**: Only `app/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/` touched for this pass.
