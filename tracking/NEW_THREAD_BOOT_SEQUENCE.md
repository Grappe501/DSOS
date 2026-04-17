# DSOS New Thread Boot Sequence

This file is the operational boot order for any new AI thread taking over the DSOS build.

## Objective
Force the new thread to rebuild system understanding from doctrine + tools before coding.

## Step 0 — Load doctrine
Read the following in order:
1. `tracking/NEXT_THREAD_PROMPT.md`
2. `tracking/current_state.json`
3. `tracking/progress.json`
4. `tracking/handoff_state_snapshot.json`
5. `tracking/THREAD_MEMORY_COMPRESSION.md`
6. `tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.8.0.md`
7. `tracking/micro_steps.json`
8. `tracking/CLEAN_SYSTEM_PROTOCOL.md`
9. `tracking/malone/MALONE_V1_MASTER_PLAN.md`
10. `tracking/malone/malone_manifest_v1.json`
11. `tracking/malone/malone_build_sequence_v1.json`

## Step 1 — Run live mapper, bootstrap, and size tools
Run:
- `python tools/project_map_audit.py`
- `python tools/self_verify_bootstrap.py`
- `python tools/scaffold_size_audit.py`
- `python scripts/build_map.py`
- `python scripts/update_progress.py`

Do not code until all outputs are reviewed.

## Step 2 — Reconcile tracking with live code
Explicitly answer:
- what is working
- what is partial
- what is stubbed
- what drift exists between tracking and code
- which roots are active and passive
- what the safest bounded next slice is

## Step 3 — Protect the live system
Preserve:
- auth and RBAC
- schedules
- proposal persistence
- Malone chat
- render verification
- deterministic fallback
- governed web retrieval
- Malone UI output-first behavior
- workflow package split direction

## Step 4 — Enforce source-of-truth roots
Treat these as active unless runtime proof says otherwise:
- backend: `app/`
- frontend: `src/`

Treat these as passive until reconciled:
- `backend/app/`
- `frontend/src/`
- `dsos_replacements/`

Exclude these from structural reasoning unless the task specifically requires them:
- `.git/`
- `.venv/`
- `node_modules/`

## Step 5 — Choose one bounded slice
Preferred order:
1. workflow package split completion
2. approval workflow completion
3. pending clarification conversation state
4. internal DSOS retrieval layer
5. department-aware governed execution
6. migration standardization

## Step 6 — Delivery standard
Return only:
- readiness audit
- chosen slice
- risk check
- full production-grade file replacements
- updated tracking files

Never return snippet-only merge instructions for production work.
