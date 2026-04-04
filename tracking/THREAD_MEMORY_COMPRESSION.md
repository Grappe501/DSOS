# DSOS — THREAD MEMORY COMPRESSION LAYER

This file is a compact continuity map for future AI thread transitions.

Use this only **after** reading:
- `/tracking/current_state.json`
- `/tracking/progress.json`
- `/tracking/NEXT_THREAD_PROMPT.md`
- `/tracking/malone/MALONE_V1_MASTER_PLAN.md`

Its purpose is to compress the architecture and current state into a form that can be reloaded quickly without losing design intent.

---

## 1. SYSTEM IDENTITY

**System Name:** DSOS / AllCare Pharmacy OS  
**Architecture Type:** Deterministic core + AI orchestration layer  
**Primary AI Layer:** Malone  
**Primary Doctrine:** AI proposes, deterministic logic validates, no black boxes

---

## 2. NON-NEGOTIABLE DOCTRINE

### Deterministic Core
The deterministic core is the truth engine.
It owns:
- validation
- execution
- permissions
- state transitions
- audit logging
- durable truth

### AI Layer
Malone is an orchestration layer.
It may:
- interpret intent
- simulate
- draft
- analyze
- propose
- coordinate sub-agents

It may **not**:
- directly commit truth
- bypass validation
- mutate state outside deterministic rules

### Validation Law
Every meaningful action must pass through:
1. intent classification
2. proposal creation
3. deterministic validation
4. optional approval
5. execution
6. audit

---

## 3. CURRENT IMPLEMENTED REALITY

### Working backend
- FastAPI runtime boots locally
- JWT auth works
- RBAC v1 works
- schedule list works
- schedule cancel flow exists
- audit routes exist
- Malone routes are wired
- Malone validation + safe execution bridge exists for schedule reads

### Working frontend
- React/Vite boots locally
- login works
- dashboard renders
- schedules page renders
- Malone page renders
- Malone chat returns proposal/validation/result

### Partially complete
- workflow/messages/events are visible but still shallow operationally
- Phase 3 tracking is close to complete but documentation can drift behind code
- Malone v1 is scaffolded and partially executing, but not yet a full agent system

---

## 4. CURRENT DESIGN TRAJECTORY

### Immediate trajectory
Move from:
- Malone proposal only
to:
- Malone validated execution
to:
- Malone bounded agent orchestration

### Build philosophy
Everything is built from reusable blocks:

blocks -> strings -> features -> functions -> workflows -> modules -> dashboards

### Long-term target
A voice-first deterministic AI operating system capable of:
- self-improvement
- bounded agent replication
- report generation
- workflow design
- external API interaction
- future local GPU / transformer integration

---

## 5. CRITICAL FILES TO PRESERVE

### Tracking
- `/tracking/current_state.json`
- `/tracking/progress.json`
- `/tracking/NEXT_THREAD_PROMPT.md`
- `/tracking/HANDOFF_MIGRATION_MESSAGE.md`
- `/tracking/handoff_state_snapshot.json`
- `/tracking/malone/MALONE_V1_MASTER_PLAN.md`
- `/tracking/malone/malone_manifest_v1.json`

### Tooling
- `/tools/project_map_audit.py`
- `/tools/scaffold_next_phase.py`
- `/tools/scaffold_malone_phase.py`

### Core backend
- `/app/main.py`
- `/app/api/routes.py`
- `/app/api/auth_routes.py`
- `/app/api/malone_routes.py`
- `/app/services/schedule_service.py`
- `/app/services/malone_service.py`
- `/app/services/intent_service.py`
- `/app/services/proposal_service.py`

### Core frontend
- `/src/App.jsx`
- `/src/lib/api.js`
- `/src/lib/maloneApi.js`
- `/src/pages/SchedulesPage.jsx`
- `/src/pages/MalonePage.jsx`
- `/src/components/malone/ChatPanel.jsx`

---

## 6. OPERATING RULES FOR FUTURE THREADS

### Never do this
- do not re-architect the system without checking tracking
- do not let AI bypass deterministic validation
- do not move executable tools into `/tracking`
- do not move doctrine/manifests into `/tools`
- do not break auth, schedules, or Malone

### Always do this
- read tracking first
- run the project map audit first
- identify drift before coding
- preserve working flows
- prefer full-file replacements

---

## 7. MALONE SUMMARY

Malone currently has:
- a page in the UI
- a backend route
- intent classification
- proposal envelope generation
- deterministic validation
- safe schedule-read execution path

Malone does **not yet** fully have:
- proposal persistence
- approval queue
- real multi-agent lifecycle
- voice execution
- write execution for schedules or workflows
- full operational intelligence layer

---

## 8. NEXT HIGH-VALUE BUILD OPTIONS

Pick only one at a time:
1. Malone -> validated schedule create execution
2. approval workflow foundation
3. department-aware Malone execution
4. proposal persistence + audit enhancement
5. workflow engine real implementation

---

## 9. IF YOU ONLY REMEMBER ONE THING

This is not a chatbot project.

This is a deterministic operating system with an AI orchestration layer.

Truth lives below.
Possibility lives above.
Nothing crosses the boundary without validation.
