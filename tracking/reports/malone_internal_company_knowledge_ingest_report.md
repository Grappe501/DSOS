# Malone internal company knowledge ingest — pass report

## 1. WHY AN INTERNAL COMPANY KNOWLEDGE INGEST PASS IS NEEDED

AllCare’s Malone stack already ingests lawbooks and can run business sources through the **ingestion control plane**, but internal company documents (policies, SOPs, training, forms, billing notes, etc.) need a **repeatable, auditable path** from disk to registered sources—without a second ingestion system or silent memory injection. This pass wires a **deterministic intake folder**, classification, and orchestration into `run_business_ingest`, with manifests and reports for governance and review handoff.

## 2. CURRENT COMPANY-KNOWLEDGE INGEST LIMITATIONS

Before this pass, operators could run `tools/run_business_ingest.py` per file with manual flags, but there was **no standard tree**, **no batch manifest**, and **no unified classification** from folder layout. Internal content was not treated as a first-class **intake product** with consistent stable keys, review recommendations, and batch validation status.

## 3. TARGET INTERNAL INGEST ARCHITECTURE

- **Single control plane** — all ingests call `run_business_ingest` (same jobs, registry, validation, optional promotion).
- **Deterministic intake root** — default `tracking/data/internal_company_knowledge/` with first-level folders mapped to `source_type` + parser profile.
- **Orchestration layer** — `app/services/internal_company_ingest/orchestration.py` scans, classifies, optionally ingests, optionally runs **policy_manual_v1** normalization for `policy_manual` and `sop_workflow` segment stores, and writes aggregate JSON.
- **CLI** — `tools/run_internal_company_ingest.py` (`--dry-run` default, `--ingest` for real runs, `--promotion` forwarded conservatively as `none` by default).

## 4. INTAKE / DISCOVERY STRATEGY

`intake_discovery.discover_intake_files` walks the intake root, skips dotfiles and `README.md`, sorts paths, and records the **first path segment** as the folder category. Files directly under the root are classified with an empty folder segment (defaults to `general_reference` with warning).

## 5. SOURCE-TYPE CLASSIFICATION + CONTROL-PLANE MAPPING

`classification.FOLDER_MAP` maps default folder names to existing `source_type` and `parser_profile_key` values (see `malone_internal_company_source_classification.md`). **No ML**: rules use folder name, filename/extension, and optional UTF-8 preview snippets for explainable hints. PDF/DOCX are marked **inactive** for generic text ingest until converted.

## 6. VALIDATION / REVIEW / PROMOTION MODEL

- Per-file validation comes from existing **ingestion validation** (`PASS` / `PASS_WITH_WARNINGS` / `FAIL`).
- Batch status uses `decide_overall_status` over collected failures/warnings (e.g. empty tree → warning).
- **Promotion** defaults to **`none`**; operators may pass `--promotion if_pass` when appropriate.
- Manifest entries carry **`review_recommendation`**, **`ingestion_priority`**, and **`review_handoff`** hints pointing at `ingestion_source_version` for the **human review API** (no auto-promote-all).

## 7. WHAT THIS PASS IMPLEMENTED

- Package `app/services/internal_company_ingest/` (discovery, classification, manifest builder, orchestration).
- Tool `tools/run_internal_company_ingest.py`.
- Sample intake tree under `tracking/data/internal_company_knowledge/` (excluding root `README.md` from ingest scan).
- Aggregate manifest output path: `tracking/ingestion_packs/internal_company_knowledge/internal_company_knowledge_manifest.json` and run report `tracking/reports/internal_company_ingest_last_run.json`.
- Tests `tests/test_internal_company_ingest.py`.

## 8. WHAT REMAINS DEFERRED

- PDF/DOCX text extraction in-pipeline (currently blocked with explicit notes).
- Dedicated `form_template` parser profile (today: `general_reference` executor with `form_template` registry type).
- Full **workflow_extraction** wiring post-ingest (readiness documented; not auto-run for every file).
- Per-department RBAC on intake folders.

## 9. HARD-FAIL COMPLIANCE CHECK

| Rule | Status |
|------|--------|
| No second ingestion platform | **Pass** — uses `run_business_ingest` only |
| Source registration + jobs | **Pass** |
| No silent Malone memory injection | **Pass** — DB-backed sources only |
| Validation + review handoff | **Pass** — manifest + review hints |
| No blanket auto-promotion | **Pass** — default `promotion=none` |
| Tracking outputs | **Pass** — reports + manifests |
