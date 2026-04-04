# DSOS / AllCare Pharmacy
## Malone v1 Master Plan — Updated for Deterministic Brain v2 Foundation

## Purpose
This document is the source-of-truth build plan for Malone’s evolution from a bounded orchestration layer into a world-class governed operational intelligence system.

The target is not a chatbot inside the app.
The target is a production-safe AI operating layer that can be studied as a model for deterministic enterprise AI.

---

## 1. Strategic objective
Build Malone into a ChatGPT-class operational assistant while preserving deterministic truth, permission control, audited execution, and production safety.

Malone must eventually be able to:
- understand natural language requests across the whole system
- retrieve current and internal knowledge
- ask clarifying questions when needed
- explain system state in plain language
- propose governed actions
- orchestrate tools and subordinate agents
- operate in voice-first environments
- remain subordinate to deterministic validation at every step that affects truth or state

---

## 2. Non-negotiable doctrine
### 2.1 Core law
AI proposes.  
Deterministic core validates.  
Only validated actions execute.  
Everything important is audited.

### 2.2 Separation of powers
- Deterministic core owns truth, state, permission, policy, execution, and audit.
- Malone owns interpretation, orchestration, conversational explanation, and proposal generation.
- OpenAI may enhance language, retrieval, summarization, and planning, but it never owns execution authority.

### 2.3 Delivery rule
No OpenAI-generated response is delivered to the dashboard unless it is verified against an approved truth packet or approved evidence bundle.

### 2.4 Build rule
Governance, traceability, and verification must always arrive before or with new power. Never after.

---

## 3. Current implemented baseline
Implemented now:
- intent classification
- proposal envelopes
- deterministic validation
- safe schedule read and analysis execution
- proposal persistence
- proposal lifecycle audit
- OpenAI render layer
- truth packet generation
- render verification
- deterministic fallback delivery
- governed web retrieval
- source-aware delivery
- deterministic action registry foundation
- deterministic validator foundation
- deterministic executor foundation
- capabilities discovery endpoint

Open items:
- pending clarification conversation state
- internal DSOS retrieval layer
- workflow engine foundation
- approval workflow foundation
- governed write execution
- richer tool orchestration
- multi-agent runtime
- voice runtime
- local model path

---

## 4. Stage map
### Stage 1 — Conversational rendering
Implemented.

### Stage 2 — Clarification loop
Partially implemented. Clarification-preferred behavior exists, but pending clarification state does not.

### Stage 3 — Internal retrieval
Not implemented.

### Stage 4 — Web retrieval
Implemented in governed read-only form with source-aware delivery.

### Stage 4b — Deterministic Brain v2 foundation
Implemented.
This stage introduced:
- deterministic action registry
- deterministic validator
- deterministic executor
- deterministic execution envelope persistence
- deterministic audit entity tracking
- capability discovery endpoint

This stage exists to prepare the system for workflows and approvals without rewriting existing behavior.

### Stage 5 — Workflow engine foundation
Next.
This stage should:
- reuse existing `WorkflowState`
- reuse deterministic action envelopes
- introduce workflow requested / validated / advanced / blocked semantics
- preserve all working flows
- avoid widening AI authority

### Stage 6 — Approval foundation
Planned.

### Stage 7 — Governed write execution
Planned.

### Stage 8 — Tool orchestration
Planned.

### Stage 9 — Multi-agent system
Planned.

### Stage 10 — Voice runtime
Planned.

### Stage 11 — Local model path
Planned.

---

## 5. Immediate instruction for the next thread
Before coding:
1. read tracking
2. run `python tools/project_map_audit.py`
3. run `python tools/self_verify_bootstrap.py`
4. reconcile tracking against live code
5. choose one bounded slice only

Default next slice: Workflow engine foundation.
