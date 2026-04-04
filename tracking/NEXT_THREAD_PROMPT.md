# DSOS NEXT THREAD PROMPT — MALONE GOVERNED INTELLIGENCE + WEB RETRIEVAL LOCK

You are continuing a live DSOS / AllCare Pharmacy build.

Before coding, load and honor these facts:

- This is a continuation build, not a greenfield build.
- Auth, schedules, audit logging, and Malone bounded proposal flow already work.
- Malone proposal persistence + Malone audit lifecycle expansion have been implemented.
- Malone conversational rendering, deterministic truth packets, render verification, fallback delivery, and governed web retrieval have now been implemented.
- The current priority is to preserve stability, complete the retrieval/governance layer, and move next into workflow + approval foundations without strategic drift.
- Deterministic doctrine is non-negotiable.

## Read first
1. `/tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.8.0.md`
2. `/tracking/malone/MALONE_V1_MASTER_PLAN.md`
3. `/tracking/current_state.json`
4. `/tracking/progress.json`
5. `/tracking/handoff_state_snapshot.json`
6. `/tracking/malone/malone_manifest_v1.json`
7. `/tracking/micro_steps.json`

## Core law
AI proposes.  
Deterministic core validates.  
Only validated actions execute.  
All meaningful steps are audited.  
All user-facing natural language is verified against deterministic truth packets before delivery.  
All external web-grounded responses must be source-aware and fail closed to deterministic fallback if verification fails.

## Current Malone status

### Working now
- intent classification
- proposal envelope generation
- deterministic validation
- bounded safe schedule read/analysis execution
- durable proposal persistence
- Malone lifecycle audit logging
- Malone UI proposal history
- OpenAI conversational rendering layer
- deterministic truth packet generation
- deterministic rendered-response verification
- deterministic fallback delivery path
- clarification-preferred response handling
- governed web retrieval through OpenAI web search
- source-aware UI responses
- dropdown-based technical detail display
- Malone page input/output-first UX

### Implemented but still stabilizing / expanding
- clarification refinement loop behavior
- retrieval rules and ambiguity gating
- verified source enforcement
- clean separation between delivered answer and technical proof
- audit completeness for web-enabled response flows

### Not yet implemented
- pending clarification conversation state
- internal DSOS retrieval layer
- approval workflow foundation
- governed write execution
- tool orchestration registry
- department-aware action enforcement
- workflow engine foundation
- multi-agent orchestration
- watcher agents
- voice runtime
- local-model abstraction for GPU transition

## Immediate build rule
Do not jump into broad feature coding first.  
The next implementation phase must follow the roadmap in the v0.8.0 plan.  
Build in ordered slices.  
Prefer governance and verification before power expansion.  
Do not bypass existing deterministic execution paths.  
Do not widen Malone authority before approvals and workflow controls exist.

## UI rule
Malone page should default to:
- input
- delivered answer
- sources when present

Technical proof should stay hidden unless expanded:
- truth packet
- verification
- rendered payload
- persisted proposal details
- recent proposals

## Web retrieval rule
Web access is read-only.  
Web search is permitted only through the governed Malone pipeline.  
Web-grounded answers must:
- capture sources
- pass verification
- cite verified sources in the response payload
- fall back safely if source verification fails

Malone must not:
- claim unverified external facts
- perform external writes
- imply that web results are deterministic system truth
- bypass source verification

## Build priority now
The next build work should focus on one bounded slice only, selected from the following in order of preference:

1. workflow engine foundation
2. approval workflow foundation
3. pending clarification conversation state
4. internal DSOS retrieval layer
5. department-aware governed execution

## Required output format for next coding thread
1. Readiness audit
2. Selected roadmap slice
3. Risk check
4. Full production-grade file replacements only
5. Updated tracking files

## Continuity rule
Preserve all currently working behavior:
- auth
- RBAC
- schedules
- audit logging
- Malone proposal persistence
- render verification
- fallback delivery
- web retrieval controls
- UI output-first behavior

If uncertain:
choose deterministic safety over AI power.