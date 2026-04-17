# Malone — Business-Wide Ingestion Architecture Report

**Run date:** 2026-04-16  
**Scope:** Active lane only (`app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`).

## 1. WHY A BUSINESS-WIDE INGESTION CONTROL PLANE IS NEEDED

DSOS must move beyond a single Arkansas lawbook vertical. Operational knowledge arrives as policies, SOPs, training packs, contracts, meeting notes, vendor PDFs, and forms. Without a shared control plane, each ingest becomes a one-off script with inconsistent identity, validation, tagging, and activation. A business-wide layer provides **one registry**, **one job and validation model**, **dimensional tagging**, and **promotion rules**, while **delegating** specialized parsing to existing legal pipelines (Arkansas handbook) or thin generic writers (policy markdown segments). Malone’s answer loop stays separate; this layer governs **how knowledge enters** and **when it becomes retrieval-eligible**.

## 2. CURRENT INGESTION REALITY IN THE REPO

- **Legal handbook:** `app/services/legal_ingestion/arkansas_pipeline.py` performs families → units → chunks → citations; `LegalIngestionJob` tracks runs; `legal_documents` / `legal_source_versions` anchor identity.
- **QA / status:** `app/services/legal_ingestion/ingest_validate_status.py` defines PASS / PASS_WITH_WARNINGS / FAIL from failures and warnings lists.
- **One-command lawbook QA:** `tracking/scripts/run_arkansas_handbook_ingest_validate.py` produces markdown + JSON reports (precheck, families, DB counts, retrieval probes).
- **Retrieval:** Lexical / citation-scoped retrieval remains on the legal tables; not duplicated here.
- **Gap before this pass:** No first-class **business source registry**, **non-legal segment store**, or **unified promotion** spanning legal and non-legal ingests.

## 3. TARGET INGESTION ARCHITECTURE

Layers (additive):

| Layer | Responsibility |
| --- | --- |
| **A. Source registry** | `ingestion_sources` + `ingestion_source_versions`: identity, type, domain, steward, authority tier, lifecycle, parser profile, optional link to `legal_*` rows. |
| **B. Parser profile registry (code)** | `app/services/ingestion_control/parser_profiles.py`: structure, chunking, metadata, anchors, validation expectations; execution pointers documented per profile. |
| **C. Ingest job framework** | `ingestion_jobs` + `ingestion_job_events`: status, stage, counts, optional `linked_legal_ingestion_job_id`. |
| **D. Metadata + tagging** | `ingestion_tag_definitions` (by dimension) + `ingestion_tag_assignments` (target_kind + target_id). |
| **E. Validation** | `ingestion_validations`: structured payloads + overall PASS / PASS_WITH_WARNINGS / FAIL. |
| **F. Promotion** | `ingestion_promotions` + version/source status fields; governance only. |
| **G. Retrieval readiness** | `retrieval_ready` on versions and `ingestion_segments`; legal chunks unchanged. |

Orchestration entrypoint: `run_business_ingest` in `app/services/ingestion_control/ingest_runner.py`. CLI: `tools/run_business_ingest.py`.

## 4. SOURCE TYPES AND PARSER PROFILES

**Source types** (string constants in `source_types.py`): legal handbook, policy manual, SOP/workflow, training module, contract rules, meeting memory, general reference, form template.

**Parser profiles** (keys in `parser_profiles.PARSER_PROFILES`):

- **`legal_handbook`** — Executes existing `ingest_arkansas_handbook_pdf`; links business version to `legal_document_id` / `legal_source_version_id`.
- **`policy_manual`** — Markdown/heading split into `ingestion_segments` (real implementation in this pass).
- **Scaffold profiles** (`sop_workflow`, `training_module`, `contract_rules`, `meeting_memory`, `general_reference`) — Same segment writer as policy manual until dedicated parsers exist; rules documented in profile objects.

## 5. TAGGING FRAMEWORK

Dimensional tags are **not** a flat blob. Dimensions (minimum): `domain`, `topic`, `document_type`, `role`, `action_type`, `review_state` (`tagging.TAG_DIMENSIONS`). Definitions live in `ingestion_tag_definitions` (unique per dimension + slug). Assignments reference `target_kind` (`source_version` or `segment`) and `target_id`. Helpers: `ensure_tag_definition`, `assign_tag`, `tag_source_version_from_map`.

## 6. VALIDATION FRAMEWORK

`validation.ValidationPayload` accumulates failures and warnings; `overall()` uses `decide_overall_status` from `ingest_validate_status` (same semantics as Arkansas QA). Legal profile: precheck, ingest success, DB counts (families, units, chunks, citations). Policy profile: checksum present, segment count > 0. Results persisted in `ingestion_validations` with JSON columns for precheck, structure, DB counts, retrieval (retrieval hooks reserved for future probes).

## 7. PROMOTION / ACTIVATION MODEL

States: source `lifecycle_status` (registered → active when promoted); version `status` (draft → validated → `promoted_active`, or archived/superseded). `promotion.promote_source_version` writes `ingestion_promotions` and sets `retrieval_ready` when promoting. Runner accepts `promotion_mode`: `none`, `if_pass`, `if_pass_or_warn`. This does **not** alter Malone’s answer path—only ingestion governance and retrieval flags.

## 8. WHAT THIS PASS IMPLEMENTED

- Alembic **`0005_business_ingestion_control_plane`** and reference SQL `schemas/business_ingestion_control_v0.sql`.
- ORM **`app/models/ingestion_control.py`** for all new tables.
- Package **`app/services/ingestion_control/`**: registry, profiles, jobs/events, validation, promotion, tagging, runner.
- CLI **`tools/run_business_ingest.py`** with optional JSON report under `tracking/reports/business_ingest_last_run.json`.
- Tests **`tests/test_ingestion_control.py`** (policy end-to-end + helpers).
- **`app/main.py`** and **`alembic/env.py`** register new models for `create_all` / metadata.

## 9. WHAT REMAINS DEFERRED

- Vector embeddings and hybrid retrieval for `ingestion_segments`.
- Dedicated parsers for SOP graphs, contract clauses, meeting decision extraction (beyond heading splits).
- Retrieval QA probes for business segments (parallel to Arkansas lexical probes).
- CI wiring for pinned PDF artifacts; admin “replace version” flows for duplicate `stable_key` on legal re-ingest.
- UI surfaces for stewards (intentionally minimal in this pass).

## 10. HARD-FAIL COMPLIANCE CHECK

| Check | Status |
| --- | --- |
| Modified only active lane roots | Yes (`app/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`). |
| Did not modify `backend/`, `frontend/`, `dsos_replacements/` | Yes. |
| Did not replace legal ingestion; delegates to Arkansas pipeline | Yes. |
| No second disconnected knowledge platform; links to legal where appropriate | Yes. |
| Validation + promotion concepts implemented | Yes. |
| Tracking outputs produced | Yes (this report + companion JSON + plans). |
| No UI-heavy build | Yes (CLI + services only). |
