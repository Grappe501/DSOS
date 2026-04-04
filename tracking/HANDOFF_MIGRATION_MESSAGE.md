# DSOS Single Handoff Migration Message

Paste this message into the first prompt of the new AI thread **along with the current DSOS zip upload**.

---

You are taking over an in-progress DSOS / AllCare Pharmacy build. Before proposing changes, do the following in order:

1. Read the entire `/tracking` folder in the uploaded project root before making recommendations.
2. Treat `/tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.7.0.md`, `/tracking/current_state.json`, `/tracking/progress.json`, `/tracking/malone/MALONE_V1_MASTER_PLAN.md`, and `/tracking/malone/malone_manifest_v1.json` as the governing build documents.
3. Audit the current backend and frontend implementation against the tracking documents and the current runtime behavior.
4. Preserve all working functionality. Do not regress auth, RBAC, branding, schedules, or Malone.
5. Provide exact **full-file replacements only** unless a tiny patch is truly safer.
6. Do not ask unnecessary clarifying questions if the current files already answer them. Make best production-grade forward progress.

## Core System Doctrine
- Deterministic core establishes truth.
- AI proposes, deterministic logic validates.
- No black boxes.
- All accepted state transitions must be auditable.
- Voice-first is the long-term primary interaction mode; keyboard/mouse are fallback.

## Current Build Reality
The system already includes:
- FastAPI backend
- React/Vite frontend
- JWT auth
- RBAC v1
- AllCare branding v1
- Working dashboard and schedules UI
- Workflow / Messages / Events pages
- Malone v1 foundation scaffolded and wired into the app
- Malone proposal + validation + safe schedule-read execution path
- Root scaffolding tools in `/tools`
- Tracking and Malone manifests in `/tracking`

## Immediate Takeover Requirements
- Re-read and sync tracking to the codebase if drift exists.
- Confirm current runtime state locally before major edits.
- Run the mapping/audit script in `/tools/project_map_audit.py`.
- Use the audit outputs to determine:
  - what is fully working
  - what is partially implemented
  - what is still scaffold/stub
  - what the next highest-value production step should be

## Current Highest-Priority Protocols
- No regression to `/api/auth/login`
- No regression to schedule list/create/cancel flow
- No regression to Malone page and `/api/malone/chat`
- Keep `/api/*` namespace
- Keep root `/tools` as executable tooling
- Keep `/tracking` as doctrine/manifests/handoff only

## What to deliver in the new thread
1. A concise architecture audit
2. Updated tracking recommendations if needed
3. Exact next implementation plan
4. Full-file production-grade replacements for the next step
