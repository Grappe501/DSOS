# Malone knowledge normalization layer — report

## 1. WHY THE KNOWLEDGE NORMALIZATION LAYER IS NEEDED

Raw ingestion (legal chunks, policy segments, citations) gives **retrieval-ready evidence** but not **operational semantics** at a consistent grain: what is a requirement vs. a definition, who it applies to, how strong the obligation is, and whether an exception exists. A **normalization layer** adds structured, reviewable knowledge units **above** ingestion so Malone can reason, filter, and explain policy/legal content without replacing PDFs, chunks, or ingestion jobs.

## 2. CURRENT INGESTION-ONLY LIMITATIONS

- **Structure without semantics**: Families, units, and segments encode layout and citations, not a stable `normalized_unit_type` or `requirement_level`.
- **No cross-cutting review artifact**: Ingestion validation covers checksums, counts, and promotion—**not** labeled obligations usable in agent guardrails.
- **Role and condition data** live in ad hoc `meta_json` or not at all.
- **Retrieval** finds text; it does not emit **governed** knowledge records for workflows.

## 3. TARGET NORMALIZATION ARCHITECTURE

- **Persistence**: `normalization_runs` → `normalized_knowledge_units` (+ optional `normalized_knowledge_review_events`).
- **Linkage**: Nullable FKs to `ingestion_*`, `legal_*`, and chunk/segment ids; JSON for citation keys and anchors.
- **Profiles**: `legal_handbook_v1`, `policy_manual_v1` (registry-driven).
- **Services**: Deterministic extractors + runners; validation uses PASS / PASS_WITH_WARNINGS / FAIL (see `normalization_validation.py`).
- **Non-goals (this pass)**: No embedding pipeline, no replacement of `ingestion_control` or legal retrieval.

## 4. NORMALIZED UNIT TAXONOMY

See `tracking/reports/malone_normalized_unit_taxonomy.md`. Core types include `definition`, `requirement`, `prohibition`, `permission`, `exception`, `escalation_rule`, `documentation_rule`, `reporting_rule`, `policy_rule`, and `general_statement`, with orthogonal **action** and **requirement_level** fields.

## 5. LEGAL AND POLICY NORMALIZATION PATHS

- **Legal (`legal_handbook_v1`)**: Iterates `legal_unit_chunks` for a `legal_source_version_id`, classifies chunk text with keyword rules, stores chunk + citation linkage. Details: `malone_legal_normalization_plan.md`.
- **Policy (`policy_manual_v1`)**: Iterates `ingestion_segments` for a version + source id, classifies segment bodies, reads optional role from segment `meta_json`. Details: `malone_policy_normalization_plan.md`.
- **Scaffolded (not executed here)**: Other `source_types` can add profiles and builder modules following the same pattern.

## 6. VALIDATION AND REVIEW MODEL

- **Run-level validation**: `source_resolved`, `unit_count`, orphan link checks, missing-summary warnings → PASS / PASS_WITH_WARNINGS / FAIL.
- **Review states**: `draft`, `system_generated`, `reviewed`, `approved`, `rejected`, `superseded` (default `system_generated` for generated units).
- **Audit**: `normalized_knowledge_review_events` for state transitions. Governance narrative: `malone_normalization_review_governance.md`.

## 7. WHAT THIS PASS IMPLEMENTED

- **Schema**: Alembic `0006_knowledge_normalization_layer`; reference `schemas/knowledge_normalization_v0.sql`.
- **Models**: `app/models/knowledge_normalization.py`.
- **Services**: `app/services/knowledge_normalization/` (unit types, registry, legal/policy normalizers, extractors, confidence, validation, source linking, serialization, runner).
- **CLI**: `tools/run_knowledge_normalization.py` (writes `tracking/reports/knowledge_normalization_last_run.json`).
- **Tests**: `tests/test_knowledge_normalization.py` (extractors, validation, policy e2e with ingest).
- **Reports**: State JSON + architecture, taxonomy, legal/policy plans, governance, this report, next-thread prompt.

## 8. WHAT REMAINS DEFERRED

- Rich **SOP / workflow graph** normalization (`workflow_step` as graph).
- **Semantic role extraction** beyond segment meta.
- **UI** for browsing/reviewing units (API not wired to `src/` in this pass).
- **Automatic review promotion** and integration with Malone chat prompts.
- **Vector / hybrid retrieval** over `retrieval_blob` (fields reserved, not indexed here).
- **Cross-reference resolution** between normalized exceptions and primary duties.

## 9. HARD-FAIL COMPLIANCE CHECK

- **Did not modify** `backend/`, `frontend/`, or `dsos_replacements/`.
- **Did not replace** ingestion control plane, legal retrieval, or evidence tables.
- **Source linkage** is first-class (FKs + JSON); **source_text** retained on each unit.
- **Opaque ML** not used; behavior is **inspectable** from code + JSON facets.
- **Validation and review** concepts are implemented and documented.
- **Tracking outputs** produced under `tracking/reports/`.
