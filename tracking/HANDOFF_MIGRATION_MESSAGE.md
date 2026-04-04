# DSOS Single Handoff Migration Message — v0.9.0

Paste this message into the first prompt of the new AI thread together with the current DSOS zip upload.

---

You are taking over an in-progress DSOS / AllCare Pharmacy build. This is a continuation build, not a greenfield build.

Before proposing or writing code, do the following in order:

1. Read the entire `/tracking` folder, starting with:
   - `/tracking/NEXT_THREAD_PROMPT.md`
   - `/tracking/NEW_THREAD_BOOT_SEQUENCE.md`
   - `/tracking/current_state.json`
   - `/tracking/progress.json`
   - `/tracking/handoff_state_snapshot.json`
   - `/tracking/THREAD_MEMORY_COMPRESSION.md`
   - `/tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.8.0.md`
   - `/tracking/malone/MALONE_V1_MASTER_PLAN.md`
   - `/tracking/malone/malone_manifest_v1.json`
   - `/tracking/malone/malone_build_sequence_v1.json`
   - `/tracking/micro_steps.json`

2. Treat the tracking folder as the governing doctrine and handoff source of truth unless the live mapper/bootstrap audits prove drift.

3. Before making recommendations or edits, run:
   - `python tools/project_map_audit.py`
   - `python tools/self_verify_bootstrap.py`

4. Use the audit outputs to determine:
   - what is fully working
   - what is partially implemented
   - what is still scaffold or stub
   - what drift exists between tracking and live code
   - what the safest single next production slice should be

5. Preserve all working functionality. Do not regress:
   - auth
   - RBAC
   - schedules
   - Malone chat
   - proposal persistence
   - render verification
   - deterministic fallback
   - web retrieval controls
   - Malone output-first UI

6. Provide exact full-file production-grade replacements only.

## Core system doctrine
- Deterministic core establishes truth.
- AI proposes, deterministic logic validates.
- Only validated actions execute.
- All accepted state transitions must be auditable.
- Voice-first is the long-term primary interaction model.
- Web-grounded answers must be source-aware and fail closed if verification fails.

## Current build reality
The system already includes:
- FastAPI backend
- React/Vite frontend
- JWT auth
- RBAC v1
- AllCare branding v1
- working dashboard and schedules UI
- workflow/messages/events visibility slices
- Malone proposal + validation + safe execution path
- proposal persistence
- lifecycle audit logging
- OpenAI render layer
- truth packet generation
- render verification
- deterministic fallback
- governed web retrieval
- output-first Malone UI
- deterministic registry foundation
- deterministic validator + executor foundations
- Malone capability discovery endpoint

## Highest-priority next protocol
After audits, default to:
1. workflow engine foundation
2. approval workflow foundation
3. pending clarification conversation state
4. internal DSOS retrieval layer
5. department-aware governed execution

## What to deliver in the new thread
1. readiness audit
2. mapper/bootstrap findings
3. selected bounded next slice
4. risk check
5. full-file production-grade replacements
6. updated tracking files
