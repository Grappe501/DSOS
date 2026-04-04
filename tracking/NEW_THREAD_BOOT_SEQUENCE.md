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
8. `tracking/malone/MALONE_V1_MASTER_PLAN.md`
9. `tracking/malone/malone_manifest_v1.json`
10. `tracking/malone/malone_build_sequence_v1.json`

## Step 1 — Run live mapper and bootstrap tools
Run:
- `python tools/project_map_audit.py`
- `python tools/self_verify_bootstrap.py`

Do not code until both are reviewed.

## Step 2 — Reconcile tracking with live code
Explicitly answer:
- what is working
- what is partial
- what is stubbed
- what drift exists between tracking and code
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

## Step 4 — Choose one bounded slice
Preferred order:
1. workflow engine foundation
2. approval workflow foundation
3. pending clarification conversation state
4. internal DSOS retrieval layer
5. department-aware governed execution

## Step 5 — Delivery standard
Return only:
- readiness audit
- chosen slice
- risk check
- full production-grade file replacements
- updated tracking files

Never return snippet-only merge instructions for production work.
