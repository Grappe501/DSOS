# DSOS Thread Memory Compression — v0.9.0

## System identity
DSOS / AllCare Pharmacy is a governed operating system with a deterministic core and an AI orchestration layer named Malone.

## Non-negotiable doctrine
- AI proposes.
- Deterministic core validates.
- Only validated actions execute.
- All meaningful actions are audited.
- All user-facing language is verified against deterministic truth or verified evidence bundles before delivery.

## Live architecture summary
### Backend
- FastAPI
- API namespace under `/api/*`
- auth, schedules, Malone, workflow/messages/events visibility slices
- SQLAlchemy models include `WorkflowState`, `AuditLog`, `MaloneProposal`, `Schedule`

### Frontend
- React/Vite
- Malone page defaults to input + delivered output
- technical proof hidden behind dropdowns
- sources shown when present

### Malone pipeline
1. intent classification
2. proposal envelope generation
3. deterministic validation
4. deterministic action resolution
5. deterministic execution
6. truth packet assembly
7. OpenAI rendering
8. render verification
9. verified delivery or deterministic fallback
10. full audit trace

## Current deterministic brain status
Implemented:
- deterministic action registry foundation
- deterministic validator foundation
- deterministic executor foundation
- schedule.read deterministic action
- schedule.analyze deterministic action
- deterministic audit entity tracking
- capabilities discovery endpoint

Not yet implemented:
- workflow engine foundation
- approval workflow foundation
- governed write execution
- internal DSOS retrieval layer
- pending clarification conversation state
- richer department-aware policy rules

## Current Malone status
Implemented:
- proposal persistence
- lifecycle audit logging
- render verification
- governed web retrieval
- source-aware delivery
- deterministic fallback
- capabilities endpoint

## Immediate next-build preference
Workflow engine foundation should land next, using:
- deterministic registry
- deterministic execution envelope
- existing WorkflowState model
- audit-first design
- no expansion of AI authority
