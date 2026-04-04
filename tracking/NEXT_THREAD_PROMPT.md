# DSOS NEXT THREAD PROMPT — DETERMINISTIC BRAIN V2 FOUNDATION LOCK

You are continuing a live DSOS / AllCare Pharmacy build.

This is a continuation build, not a greenfield build.

Before proposing or writing code, you must first reconstruct the live system state from tracking and tools.

## Mandatory read order
1. `/tracking/NEXT_THREAD_PROMPT.md`
2. `/tracking/NEW_THREAD_BOOT_SEQUENCE.md`
3. `/tracking/current_state.json`
4. `/tracking/progress.json`
5. `/tracking/handoff_state_snapshot.json`
6. `/tracking/THREAD_MEMORY_COMPRESSION.md`
7. `/tracking/HANDOFF_MIGRATION_MESSAGE.md`
8. `/tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.8.0.md`
9. `/tracking/micro_steps.json`
10. `/tracking/malone/MALONE_V1_MASTER_PLAN.md`
11. `/tracking/malone/malone_manifest_v1.json`
12. `/tracking/malone/malone_build_sequence_v1.json`

## Mandatory tool boot
Run both before any coding:
- `python tools/project_map_audit.py`
- `python tools/self_verify_bootstrap.py`

If either fails, stop and report the failure before changing code.

## Core doctrine
- AI proposes.
- Deterministic core validates.
- Only validated actions execute.
- All meaningful steps are audited.
- All delivered natural language is verified against deterministic truth or verified evidence bundles.
- Web-grounded responses must be source-aware and fail closed to deterministic fallback if verification fails.

## Current live system understanding
Working now:
- auth, RBAC, dashboard, schedules
- Malone proposal flow
- proposal persistence and audit lifecycle
- OpenAI render layer behind backend-only configuration
- truth packet generation
- render verification and deterministic fallback
- governed web retrieval and source-aware delivery
- Malone UI output-first presentation with hidden technical proof
- deterministic action registry foundation
- deterministic validator and deterministic executor foundations
- Malone capability discovery endpoint

Not yet implemented:
- workflow engine foundation
- pending clarification conversation state
- internal DSOS retrieval layer
- approval workflow foundation
- governed write execution
- tool orchestration registry beyond current deterministic registry
- multi-agent runtime
- voice runtime
- local-model abstraction for GPU transition

## Immediate build rule
Do not jump into broad feature coding first.
Use the mapper and bootstrap tools to confirm live state.
Then choose one bounded next slice only.

Default next slice priority:
1. workflow engine foundation
2. approval workflow foundation
3. pending clarification conversation state
4. internal DSOS retrieval layer
5. department-aware governed execution

## Output format required from the next thread
1. readiness audit
2. mapper/bootstrap findings
3. selected next slice
4. risk check
5. full production-grade file replacements only
6. updated tracking files

## Non-regression guard
Do not regress:
- `/api/auth/login`
- schedule list/create/cancel flow
- `/api/malone/chat`
- proposal persistence
- render verification
- deterministic fallback
- web retrieval controls
- Malone output-first UI

If uncertain, choose deterministic safety over AI power.
