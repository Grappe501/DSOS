# Malone — deeper SOP / workflow extraction & assembly

## 1. WHY DEEPER SOP / WORKFLOW EXTRACTION IS NEEDED

Normalized units and coarse workflow assembly already power decision/workflow and the operating copilot, but **operational reliability** depends on surfacing **ordered steps, checkpoints, stops, escalations, and ownership** when the underlying text supports them. Without inspectable text extraction, Malone cannot distinguish a thin bullet list from a rigorous SOP with explicit stop/escalate points.

## 2. CURRENT OPERATING COPILOT LIMITATIONS

The operating copilot consumed `action_steps` built mainly from normalized unit summaries and ordering heuristics. **Checkpoints, prerequisites, and stop conditions** were only indirectly visible when normalization already captured them; regex-level signals on the same text surface were not systematically extracted or merged into the decision block.

## 3. TARGET SOP / WORKFLOW EXTRACTION ARCHITECTURE

Package **`app/services/workflow_extraction/`** applies **deterministic, explainable** patterns (numbered lists, bullets, prerequisite headers, checkpoint/stop/escalation phrases, role terms, simple conditionals, output verbs) to **unit title + plain_language_summary** via `combined_unit_text`. Output is JSON-safe under `extract_workflow_fields_from_text`, with an **`extraction_confidence`** score (`high` / `medium` / `low`).

## 4. TARGET WORKFLOW ASSEMBLY ARCHITECTURE

Package **`app/services/workflow_assembly/`** enriches each `action_step` after `assemble_ordered_steps` with a **`workflow_extraction`** payload, resolves **ownership** (`merge_step_ownership`: normalized `applies_to_role` wins; else first text role hint; else unknown), and augments the decision plan with **`workflow_checkpoint_view`**, **`workflow_branch_hints`**, **`workflow_escalation_lines_merged`**, and **`workflow_extraction_assessment`** (sparse-signal fallback flag).

## 5. ROLE / CHECKPOINT / STOP / BRANCH MODEL

- **Roles:** Regex buckets (pharmacist, technician, PIC, nurse, compliance) with evidence spans; never invented titles.
- **Checkpoints / stops / escalations:** Sentence-level regex captures; surfaced in merged flat lists and appended to copilot next-step lines when present.
- **Branches:** Simple `if` / `unless` / `when` sentence captures — **no executable workflow engine**.

## 6. POLICY + SOP + LEGAL INTERACTION IN THIS PASS

- **SOP + policy:** Same merged units as before; extraction runs on each step’s unit text regardless of lane. Policy prose that reads like a procedure contributes numbered/bullet steps like SOP text.
- **Legal:** Legal lookup and citation-first formatting are **unchanged**. Legal units may receive extraction metadata but **must not** be reinterpreted as procedural certainty; guardrails reinforce this when extraction is weak.

## 7. FALLBACK / SAFETY MODEL

- **`workflow_extraction_assessment.use_minimal_workflow_guidance`**: true when `partial_workflow` and no high-confidence extractions across steps (sparse signals).
- **Truth packet:** When minimal guidance applies, extra **forbidden_claims** warn against over-trusting regex-derived checkpoints (`workflow_extraction_weak_signal_forbidden_claims`).
- **Copilot:** Still defers to uncertainty and existing copilot fallbacks; does not fabricate full procedures.

## 8. WHAT THIS PASS IMPLEMENTED

- `workflow_extraction` + `workflow_assembly` packages; integration in `build_action_plan` (`enrich_action_steps_with_extraction`, `augment_decision_plan_with_assembly`).
- Operating copilot next-step lines optionally append short **stop/checkpoint** hints from extraction.
- Guardrails + `enrich_truth_packet_with_decision_workflow` extension for weak extraction.
- Tests: `tests/test_workflow_extraction_assembly.py`; debug: `tools/debug_workflow_extraction.py`.

## 9. WHAT REMAINS DEFERRED

- ML/LLM parsers; PDF layout-aware extraction.
- Splitting a single normalized unit into multiple ordered steps in the graph (currently **embedded numbered substeps** are counted, not expanded as separate graph nodes).
- Deep cross-unit dependency graphs beyond ordering.

## 10. HARD-FAIL COMPLIANCE CHECK

- **One Malone path:** Enrichment is inside existing `build_action_plan` / truth packet only.
- **Source-grounded:** Extraction runs on **provided unit text** only; null/empty fields when unsupported.
- **Legal:** Citation-first path preserved; tests assert formatter still shows citations.
- **No second engine:** Regex assembly augments dicts; no separate runtime workflow executor.
