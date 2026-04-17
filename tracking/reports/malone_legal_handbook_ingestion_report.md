# Malone Legal Handbook Ingestion — Foundation Report

**Scope:** Deterministic legal-ingestion foundation for the Arkansas State Board of Pharmacy compiled “Statutes and Rules” handbook (November 2025 cover example), not a chatbot or generic document pipeline.

**Repository lane:** `app/`, `schemas/`, `alembic/`, `tracking/` only for this pass.

---

## 1. ACTIVE-LANE MALONE REALITY

### What Malone currently does

- **HTTP surface:** `app/api/malone_routes.py` exposes `/api/malone/chat`, proposals, capabilities, and an empty agents list. Chat calls `handle_malone_request` in `app/services/malone_service.py`.
- **Core loop:** Intent classification → proposal envelope → validation → workflow instance (default workflow) → deterministic execution where applicable → **`build_truth_packet`** (`truth_packet_service`) → OpenAI render when configured → **`verify_rendered_response`** → delivery with verification payload.
- **Truth and safety:** `truth_packet_service` constrains allowed claims and web-search rules; `render_verifier` enforces grounding. Clarification and approval paths exist as services (`clarification_service`, `approval_service`) and workflow hooks.

### What existing services should remain untouched in this pass

- **Do not refactor:** `malone_service` orchestration, `intent_service`, `proposal_service`, `workflow_service` / `workflows/*`, `openai_service`, `render_verifier`, `deterministic_*`, auth, schedules API.
- **Regulation foundation:** `schemas/regulation_knowledge_v0.sql` and migration `0002_regulation_knowledge_foundation` remain the generic regulation spine; this pass **adds** handbook-specific `legal_*` tables and `legal_*` service packages without removing prior work.

### Where legal ingestion should plug in

- **Ingestion (future):** Batch/admin job writes rows into `legal_*` tables; no change to Malone chat until an explicit intent routes “pharmacy law / handbook” queries through a new evidence path.
- **Retrieval (future):** `legal_retrieval/*` returns ranked chunks + `citation_key` lists for a proposed extension to **`build_truth_packet`** (e.g. `retrieval_rules.internal_legal_chunks`) so rendered answers remain verifier-compatible.
- **Traceability:** `legal_answer_traces` links to `malone_proposals.id` the same way `regulation_answer_traces` does, preserving audit symmetry.

---

## 2. WHAT THIS LEGAL HANDBOOK REQUIRES

### Why this PDF cannot be ingested as a generic document

- The file is a **compiled multi-authority handbook**: multiple **source families** (TOC sections labeled A–H), not a single linear narrative.
- **Legal identity** is carried by **citations** (e.g. `17-92-101`, `5-64-101`) and **rule section headings** (“Section I”, “Section II”), not by page order alone.
- **Subsection structure** (`(a)`, `(1)`, `(A)`, `(i)`) is part of the meaning; flattening loses the subsection path users must see in answers.
- **Cross-references** point across families and authorities; they must be extracted and optionally resolved for navigation and audit.

### Why hierarchy, citations, authority typing, and date layering matter

- **Hierarchy:** Answers must cite **family → unit → subsection path** so users know *which part of the book* and *which legal unit* (statute vs board rule).
- **Citations:** Retrieval and UI need stable **`citation_key`** values and **`anchor_json`** (page, offsets) for deterministic replay.
- **Authority typing:** The same handbook mixes **Arkansas Code** provisions and **board rules**; conflating them breaks user trust and compliance framing.
- **Date layering:** The **cover edition** (e.g. November 2025) is not the same as **embedded act revision labels** inside families (e.g. Pharmacy Practice Act May 2023 vs Uniform Controlled Substances Act August 2025). The system must store both **compiled edition** and **per-family embedded dates** without collapsing them into one field.

---

## 3. LEGAL INGESTION PROFILE

### File-level metadata

- **Storage:** `storage_uri`, `content_checksum`, `original_filename`.
- **Cover:** `compiled_edition_label` (e.g. November 2025), `cover_metadata_json` (board name, title string).
- **Status:** `legal_documents.status` drives ingestion state machine.

### Section-family parsing

- Parse TOC to **`legal_document_families`**: `family_code` (A–H), `title`, `toc_page_start` / `toc_page_end`, `embedded_source_revision_label` when printed in that family’s header.

### Legal-unit detection

- **Statute blocks:** Pattern-detect Ark. Code-style sections (`\d+-\d+-\d+`) and associate with headings.
- **Rule sections:** Detect “Section I / II …” and board-rule numbering consistent with the handbook’s own convention.
- **Tree:** `legal_units.parent_legal_unit_id` preserves nested structure under a family.

### Subsection-preserving chunking

- **`subsection_parser`** emits ordered segments; **`chunk_builder`** writes **`legal_unit_chunks`** with **`subsection_path`** aligned to `(a)(1)(A)(i)` depth.
- Chunks are the **retrieval unit**; units are the **legal identity** node.

### Cross-reference extraction

- **`cross_reference_extractor`** fills **`legal_cross_references`** with `raw_reference_text`, optional `to_citation_key`, `resolution_status` until a linker pass resolves `to_legal_unit_id`.

### Mixed-date handling

- **`date_layering`** (and **`legal_date_layers`**) records:
  - compiled edition (document scope),
  - embedded family labels (family scope),
  - optional unit-scoped effective notes when explicitly printed.

---

## 4. DATA MODEL RECOMMENDATION

| Concept | Table(s) | Notes |
|--------|------------|--------|
| Uploaded documents | `legal_documents` | One row per handbook file / stable logical identity. |
| Document families / major sections | `legal_document_families` | A–H TOC partitions with optional page spans. |
| Edition / ingest snapshots | `legal_source_versions` | Checksum or label changes over time for the same `legal_document_id`. |
| Legal units | `legal_units` | Statute/rule nodes with `unit_kind`, `primary_citation`, hierarchy. |
| Legal chunks | `legal_unit_chunks` | Subsection-aware retrieval slices with page/char offsets. |
| Legal citations | `legal_citations` | Stable `citation_key`, `authority_type`, `anchor_json`. |
| Cross-references | `legal_cross_references` | Parsed refs and resolution state. |
| Tags / taxonomy | `legal_tags`, `legal_chunk_tags` | Controlled topics for filtering. |
| Source versions / date layers | `legal_source_versions`, `legal_date_layers` | Edition vs embedded dates vs explicit labels. |
| Ingestion jobs | `legal_ingestion_jobs` | Stage, status, errors. |
| Answer traces | `legal_answer_traces` | `proposal_id`, chunk ids, `citation_keys_json`, `verified`. |

**Bridge to existing regulation tables (optional):** `legal_knowledge/versioning.py` may later map `stable_key` to `regulation_sources` for unified admin UX; not required for v0.

---

## 5. SELF-ASSEMBLING SYSTEM FIT

- **`legal_*` packages import nothing at app startup** beyond normal module load; they do not register routes or schedulers.
- **Malone remains dormant** for legal Q&A until:
  - data exists in `legal_unit_chunks`, and
  - an intent/router path selects `legal_assistant.orchestrator` (future).
- **On demand:** Orchestrator pulls `legal_retrieval` → `legal_compliance` → `answer_formatter`; outputs feed the **existing** truth-packet + verify pipeline rather than a parallel chat stack.

---

## 6. IMPLEMENTATION ORDER

Next **12** steps (strict sequence):

1. Register uploaded PDF in `legal_documents` + initial `legal_source_version` row after checksum.
2. Extract cover and TOC text; populate `legal_document_families` (A–H) with page spans.
3. Implement `toc_parser` output → DB insert for families (deterministic tests on fixtures).
4. Per family, run `legal_unit_parser` to populate `legal_units` (statute and rule headings).
5. Run `subsection_parser` + `chunk_builder` to populate `legal_unit_chunks`.
6. Populate `legal_citations` and unique `citation_key` scheme (namespace by kind + normalized id).
7. Run `cross_reference_extractor` + linker pass for `legal_cross_references`.
8. Populate `legal_date_layers` from cover + per-family headers; validate against `embedded_source_revision_label`.
9. Add SQLite FTS or external index for `lexical.py` (if staying SQLite-first).
10. Wire `citation_lookup` + `hybrid` + `reranker` + `authority_filter` behind a single retrieval facade.
11. Extend truth-packet builder with optional `internal_legal` evidence list + `legal_answer_traces` on proposal id.
12. Add minimal admin/ingestion API or CLI **outside** Malone chat (per product decision), with job rows in `legal_ingestion_jobs`.

---

## 7. RISKS / BLOCKERS

**Repository-specific**

- **`Base.metadata.create_all` vs Alembic:** Runtime still uses `create_all` in `app/main.py`; legal tables are defined in **Alembic** and **`schemas/legal_handbook_knowledge_v0.sql`**. Teams must run **`alembic upgrade head`** for environments that rely on migrations (already applied in dev when upgrading).
- **Dual corpora:** `regulation_*` and `legal_*` coexist; product clarity is needed on whether future retrieval merges or filters by corpus.
- **No SQLAlchemy models yet:** Services are scaffold-only; ORM models would duplicate DDL until consolidated in a follow-up.

**Source-specific (Arkansas handbook)**

- **PDF structure variance:** If TOC is image-only, deterministic parsing requires an OCR stage (explicit job stage, not hidden inside Malone).
- **Citation collisions:** Similar numbers across titles require **family + citation** disambiguation in `citation_key` design.
- **Embedded vs effective law:** Handbook text may lag filings; assistant must **fail closed** on “current law outside uploaded corpus” using `legal_compliance/escalation`.

---

## Artifacts from this pass

- SQL proposal: `schemas/legal_handbook_knowledge_v0.sql`
- Migration: `alembic/versions/0003_legal_handbook_knowledge_foundation.py` (chains after `0002_regulation_knowledge_foundation`; requested `0002_legal_*` filename was reserved by existing `0002` regulation migration)
- Scaffolds: `app/services/legal_ingestion/`, `legal_knowledge/`, `legal_retrieval/`, `legal_compliance/`, `legal_assistant/`
- Tracking: `tracking/reports/malone_legal_handbook_ingestion_state.json`, `malone_legal_ingestion_module_plan.json`, companion plans linked from `NEXT_THREAD_PROMPT_LEGAL_HANDBOOK_FOUNDATION.md`
