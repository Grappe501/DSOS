# Next Thread — Legal Handbook Foundation (Continuation)

You are continuing the DSOS / Malone build in the **active lane** (`app/`, `schemas/`, `alembic/`, `tracking/`). Do **not** modify `backend/`, `frontend/`, or `dsos_replacements/`.

## What was completed

- **Reports & state:** `tracking/reports/malone_legal_handbook_ingestion_report.md`, `malone_legal_handbook_ingestion_state.json`, `malone_legal_ingestion_module_plan.json`, `malone_legal_schema_plan.md`, `legal_ingestion_profile_arkansas_pharmacy_lawbook.md`, `arkansas_lawbook_source_map_plan.md`, `malone_legal_retrieval_plan.md` (this directory).
- **SQL proposal:** `schemas/legal_handbook_knowledge_v0.sql`
- **Migration:** `alembic/versions/0003_legal_handbook_knowledge_foundation.py`  
  - **Note:** The filename `0002_legal_handbook_knowledge_foundation.py` was **not** used because `0002_regulation_knowledge_foundation` already occupies revision `0002`. Legal handbook DDL is **`0003`** with `down_revision = 0002_regulation_knowledge_foundation`.
- **Scaffolds:** `app/services/legal_ingestion/`, `legal_knowledge/`, `legal_retrieval/`, `legal_compliance/`, `legal_assistant/` (docstring-only boundaries; no fake implementations).

## Immediate next build pass (bounded)

1. Add **SQLAlchemy models** for `legal_*` tables (match migrated SQLite; use `meta_json` not `metadata`).
2. Implement **ingestion job runner** (CLI or admin-only route) that: registers PDF → runs profiler/TOC parser → persists families (still deterministic).
3. Add **fixture-based unit tests** for `toc_parser`, `legal_unit_parser`, `subsection_parser` using excerpted text from the Arkansas handbook.
4. Add **FTS** (or interim `LIKE`-scoped search) for `lexical.py` behind a feature flag.
5. **Do not** wire Malone chat until retrieval returns stable evidence bundles and traces.

## Commands to verify DB

```bash
alembic current
alembic upgrade head
```

## Design anchors

- One PDF, **families A–H**, **citations** `17-92-xxx` / `5-64-xxx`, **rule sections** “Section I…”, **subsections** `(a)(1)(A)(i)`, **mixed dates** (November 2025 cover vs May 2023 / August 2025 embedded family dates).

## Read first

- `tracking/reports/malone_legal_handbook_ingestion_report.md`
- `schemas/legal_handbook_knowledge_v0.sql`
- `app/services/malone_service.py` (truth packet + delivery only; extend later)
