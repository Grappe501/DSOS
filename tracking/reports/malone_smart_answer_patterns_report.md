# Malone smart answer patterns — report

## 1. WHY SMART ANSWER PATTERNS ARE NEEDED

Users ask **different kinds** of operational and compliance questions (obligations, procedures, exceptions, “where is this written”). A single fixed section order buries the signal. Deterministic **answer patterns** reshape presentation **after** retrieval, using the same evidence and normalized fields, so Malone answers read closer to the user’s intent without a second engine.

## 2. CURRENT ONE-SHAPE ANSWER LIMITATIONS

- Legal and policy deterministic paths used one **linear** layout (citation blocks + normalized addenda + optional decision/workflow appendix).
- Question phrasing did not influence **section emphasis** (e.g., exception-seeking vs locator-seeking).
- No compact **inspectable trace** of “which layout was chosen and why” on the truth packet.

## 3. TARGET ANSWER-PATTERN ARCHITECTURE

- Package `app/services/answer_patterns/`: `signals` (question + normalized tallies), `pattern_selector` (deterministic winner + confidence + reasons), per-pattern renderers, `integration` bridging `answer_formatter` and Malone delivery.
- **Standard** pattern preserves the legacy single-shape body when patterns are disabled, confidence is low, or fallback rules fire.
- **Truth packet** gains `answer_pattern` plus `packet_meta` keys (`answer_pattern_rendered`, `answer_pattern_selected`, `answer_pattern_confidence`).

## 4. PATTERN SELECTION STRATEGY

- **Question signals**: keyword families map to requirement / workflow / exception / source_locator scores (plus short citation-like query bias for locator).
- **Normalized signals**: unit types and presence of condition/exception/escalation text add to the same score buckets.
- **Winner**: max score among the four patterns; **tie-break order** (deterministic): source_locator → requirement → workflow → exception.
- **Zero score** across all four → `standard`.
- **Legal handbook**: if normalized units are empty and the winner would be requirement/workflow/exception with **top text score &lt; 12**, downgrade to source_locator (if locator score &gt; 0) else `standard`.

## 5. LEGAL AND POLICY SUPPORT IN THIS PASS

- **legal_handbook**: `format_legal_lookup_answer(..., message=..., truth_packet=...)` runs smart integration; citation-first content preserved inside each pattern (especially **source_locator** and standard).
- **policy_manual**: same via `format_policy_lookup_answer`; operational fields surfaced in **requirement** pattern (roles, requirement strength, conditions, etc.).
- **SOP** delivery reuses policy formatter + patterns (policy selector `source_type` in selector is still `policy_manual` for scoring — acceptable reuse; refine later if needed).

## 6. FALLBACK / SAFETY MODEL

- Env `MALONE_SMART_ANSWER_PATTERNS_ENABLED` (default **on**; set off to force legacy shape).
- `should_fallback_to_standard_pattern`: low confidence, or requirement/workflow/exception with **no** normalized units and confidence not **high** → standard body.
- Non-standard patterns add **supplementary forbidden claims** via `smart_answer_pattern_forbidden_claims`.
- No fabricated workflows: workflow pattern uses decision/workflow block when present; otherwise states partial/incomplete explicitly.

## 7. WHAT THIS PASS IMPLEMENTED

- `app/services/answer_patterns/*` (selector, signals, four pattern modules, shared formatting, integration, fallback, serialization).
- Formatter split: `format_*_lookup_answer_standard` vs smart entry with `message` + `truth_packet`.
- `malone_service` passes `message` and attaches `answer_pattern` into delivery audit `meta_json`.
- `tools/debug_answer_patterns.py`; `tests/test_answer_patterns.py`.
- Tracking suite (this report + companion notes + state JSON).

## 8. WHAT REMAINS DEFERRED

- Full implementations for **definition**, **escalation**, **comparison**, **operational summary** patterns (names reserved in state JSON only).
- LLM render path: pass `answer_pattern` into `render_conversational_response` with layout hints.
- Per–source-type tuning for SOP (`sop_workflow` selector profile).

## 9. HARD-FAIL COMPLIANCE CHECK

- **Did not modify** `backend/`, `frontend/`, or `dsos_replacements/`.
- **Did not** remove citation-first legal content from patterns; source_locator reinforces citations.
- **Did not** add a second Malone stack; selection is a formatting layer only.
- **Fallbacks** and guardrails in place.
- **Tracking outputs** produced.
