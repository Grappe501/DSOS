# Next Thread — Regulation Foundation Continuation

You are continuing the DSOS / Malone build after the **Malone Regulation Knowledge Foundation** pass (2026-04-16).

## What was completed

- Written: `tracking/reports/malone_regulation_foundation_report.md`, `malone_regulation_foundation_state.json`, `malone_regulation_module_plan.json`, `malone_regulation_schema_plan.md`, `malone_regulation_api_plan.md`.
- SQL proposal: `schemas/regulation_knowledge_v0.sql`.
- Alembic draft: `alembic/versions/0002_regulation_knowledge_foundation.py` (depends on `0001_v070_department_workflow`).
- Python scaffolds (import-only, **not wired**):  
  `app/services/ingestion/`, `knowledge/`, `retrieval/`, `compliance/`, `assistant/`.

## Active vs passive roots

- **Active:** `app/`, `src/`, `tracking/`.
- **Do not modify unless reconciling:** `backend/`, `frontend/`, `dsos_replacements/`.

## Immediate next work (bounded)

1. Verify Alembic chain and apply `0002` on dev DB; resolve any SQLite FK/column issues.
2. Add **SQLAlchemy models** for regulation tables (mirror migration; keep files small).
3. Implement **ingestion job** persistence + stub pipeline that writes **chunks** for one sample document (test fixture).
4. Implement **lexical retrieval MVP** (FTS or `LIKE` fallback) returning chunk + citation for library use.
5. **Feature-flag** an optional `regulation_evidence` block in `truth_packet_service` when retrieval returns hits—still through existing render verification.

## HARD FAIL CONDITIONS (same pass is incorrect if any are true)

- Modify `backend/`, `frontend/`, or `dsos_replacements/`.
- Replace existing Malone behavior wholesale.
- Add code with no declared integration purpose (see scaffold docstrings).
- Change schema direction away from **versioning + citations** for regulation text.
- Skip required **tracking** updates for the slice you ship.
- Ship speculative regulation Q&A **before** source registry + chunks + citations exist in DB.

Full table: `tracking/reports/malone_regulation_foundation_report.md` (section **HARD FAIL CONDITIONS**).

## Do not

- Rewrite Malone, workflows, or frontend architecture.
- Build full production chatbot or upload UI in one shot.
- Add speculative frameworks or duplicate logic in passive roots.

## Read first

- `tracking/reports/malone_regulation_foundation_report.md`
- `schemas/regulation_knowledge_v0.sql`
- `app/services/malone_service.py` and `app/services/truth_packet_service.py`

Begin by confirming DB state after migration and listing gaps between ORM and migration.
