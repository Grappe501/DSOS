# DSOS / AllCare Pharmacy
## Malone v1 Master Plan

## Purpose
This document is now the source-of-truth build plan for Malone’s evolution from a bounded internal orchestration layer into a world-class, governed operational intelligence system.

This plan does not replace DSOS doctrine.
It operationalizes it.

The target is not “a chatbot inside the app.”
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
- **Deterministic core** owns truth, state, permission, policy, execution, and audit.
- **Malone** owns interpretation, orchestration, conversational explanation, and proposal generation.
- **OpenAI layer** may enhance language, retrieval, summarization, and planning, but it never owns execution authority.

### 2.3 Delivery rule
No OpenAI-generated response is delivered to the dashboard unless it is verified against an approved truth packet or approved evidence bundle.

### 2.4 Build rule
Governance, traceability, and verification must always arrive before or with new power.
Never after.

---

## 3. Malone end-state architecture

Malone will mature into a seven-stage governed pipeline:

1. **Input normalization**  
   Accept dashboard text, future voice transcription, and system event triggers.

2. **Intent and scope determination**  
   Determine request type, actor role, department scope, target systems, and whether clarification is required.

3. **Retrieval and tool access**  
   Gather DSOS data, file evidence, web evidence, tool results, and policy context.

4. **Truth packet assembly**  
   Deterministically compile the facts Malone is allowed to speak from.

5. **LLM reasoning and rendering**  
   Use OpenAI to refine unclear questions, produce conversational responses, summarize evidence, and propose next actions.

6. **Deterministic verification**  
   Verify that the final answer or plan does not alter facts, permissions, or required compliance language.

7. **Governed execution or delivery**  
   Deliver the verified response, or route approved actions into approval and execution systems.

---

## 4. Full roadmap by stage

## Stage 0 — Existing baseline (already implemented)
### Objective
Lock the current bounded Malone foundation.

### Present now
- Malone route and UI
- intent classification
- proposal envelopes
- deterministic validation
- bounded schedule read and analysis execution
- proposal persistence
- audit lifecycle logging for proposal create / validate / execute-record

### Action
No redesign. Preserve baseline.

---

## Stage 1 — Conversational rendering layer
### Objective
Convert rigid deterministic outputs into high-quality natural language without allowing fact drift.

### What gets built
- backend OpenAI service wrapper
- environment-based OpenAI configuration
- response schema for conversational rendering
- render request object built from deterministic truth packets
- render verification pass before dashboard delivery
- fallback deterministic response when render verification fails

### What does not happen yet
- no write actions
- no approvals
- no multi-agent control
- no web search execution

### Required production controls
- server-side key only
- structured outputs only for governed response types
- response logging and audit linkage to proposal id
- deterministic claim whitelist or field-bound render strategy

### Why this comes first
It immediately improves user experience while preserving safety.

### Build timing
**Implement now in the next engineering phase.**

---

## Stage 2 — Clarification and refinement loop
### Objective
Allow Malone to ask targeted questions when user intent is ambiguous or under-specified.

### What gets built
- ambiguity detector
- clarification-required state in Malone responses
- structured clarification schema
- conversation turn state for pending clarification
- deterministic policy deciding when execution must block until clarified

### Example outcomes
- “Do you want all schedules or only pharmacy schedules?”
- “Are you asking for an explanation, a summary, or a proposed action?”

### Required production controls
- clarification cannot mutate state
- clarification must narrow scope, not broaden it
- clarification history should be auditable

### Build timing
**Implement immediately after Stage 1.**

---

## Stage 3 — Retrieval core: internal DSOS knowledge
### Objective
Give Malone grounded access to internal system knowledge before broad internet power.

### What gets built
- file/document retrieval layer for DSOS docs, SOPs, and tracking files
- retrieval adapters for internal documents
- evidence packet schema for internal knowledge
- citation / provenance storage in audit
- UI support for evidence-aware answers

### Why internal first
Internal retrieval is safer, more stable, and more directly useful for operations.

### Build timing
**Implement after clarification loop.**

---

## Stage 4 — Internet access with evidence control
### Objective
Give Malone current-information capability with auditable sourcing.

### What gets built
- backend web retrieval service
- allowlist / risk-tier rules for external domains by use case
- evidence packet format for web results
- citation-required response modes
- deterministic verifier that checks rendered answers against web evidence

### Acceptable uses
- current regulations
- public notices
- weather / closures
- payer updates
- operational news
- product / vendor research

### Restricted uses
- high-trust domain claims without evidence
- uncited medical or compliance statements
- web-derived write actions without approval

### Build timing
**Later phase, after internal retrieval and rendering verification are stable.**

---

## Stage 5 — Approval foundation
### Objective
Build the governance gate between proposals and state-changing execution.

### What gets built
- approval request model
- approval queue
- approver roles and routing rules
- approve / reject endpoints
- audit chain from proposal → approval → execution
- UI for pending approvals and decision history

### Why this precedes governed write execution
Malone must not gain write power before approval infrastructure exists.

### Build timing
**Before any write-level Malone execution.**

---

## Stage 6 — Governed write execution
### Objective
Allow Malone to propose state-changing actions that the deterministic core can execute after validation and approval.

### What gets built
- bounded action registry
- action schemas for schedule create/update/cancel and later modules
- deterministic preflight validation
- department-aware permission enforcement
- post-execution audit and result storage

### Safety rule
OpenAI never executes writes directly.
It may only produce a proposal object.

### Build timing
**Only after approval foundation is live.**

---

## Stage 7 — Tool orchestration layer
### Objective
Turn Malone into a governed operator across multiple internal and external tools.

### What gets built
- formal tool registry
- tool capabilities manifest
- tool access policy by role and department
- tool-call logging and replay record
- deterministic wrapper for every tool call

### Candidate tools
- schedules
- tasks
- workflows
- messages
- events
- audit search
- file retrieval
- web retrieval
- notifications
- external APIs

### Build timing
**After write execution governance is proven.**

---

## Stage 8 — Multi-agent system
### Objective
Allow Malone to coordinate subordinate specialists without losing governance.

### What gets built
- agent registry
- agent contracts and allowed scopes
- task delegation model
- agent-run persistence
- supervisor review and result verification

### Example agents
- report agent
- compliance watcher
- staffing agent
- SOP summarizer
- policy monitor
- vendor research agent

### Build timing
**Later phase. Not now.**

---

## Stage 9 — Voice-first runtime
### Objective
Bring Malone to natural spoken interaction for operational use.

### What gets built
- speech-to-text input pipeline
- confirmation / disambiguation flow for risky intents
- concise spoken response mode
- optional hands-free workflow support

### Build timing
**After text pipeline governance is mature.**

---

## Stage 10 — Self-improvement and in-house model pathway
### Objective
Prepare Malone to propose system improvements and eventually shift parts of intelligence in-house.

### What gets built
- proposal-based self-improvement registry
- architecture feedback loop
- model abstraction layer
- GPU-hosted future local-model adapter interface
- benchmark harness comparing local and external models

### Rule
Self-improvement proposals are suggestions, never self-applied changes.

### Build timing
**Long-range phase.**

---

## 5. What should be implemented now vs later

### Implement now
1. OpenAI backend integration
2. structured conversational render layer
3. deterministic truth packet format
4. deterministic rendered-answer verifier
5. audit expansion for render events
6. fallback path when render verification fails

### Implement next
1. clarification/refinement loop
2. conversation turn memory for pending clarification
3. internal DSOS retrieval and evidence packets

### Implement later
1. internet retrieval
2. approval foundation
3. governed write execution
4. tool orchestration
5. multi-agent system
6. voice runtime
7. self-improvement loop
8. in-house model abstraction and GPU transition

---

## 6. Required new system artifacts

## 6.1 Backend
Expected new or expanded services:
- `app/services/openai_service.py`
- `app/services/malone_render_service.py`
- `app/services/malone_truth_packet_service.py`
- `app/services/malone_verify_service.py`
- `app/services/malone_clarification_service.py` (later)
- `app/services/retrieval_service.py` (later)
- `app/services/web_retrieval_service.py` (later)

Expected new config/support files:
- environment loading for `OPENAI_API_KEY`
- render schemas
- verifier rule sets
- tool / capability manifest expansion

## 6.2 Frontend
Expected UI additions:
- conversational answer panel
- sources / evidence display
- clarification prompt UI
- render failure / fallback notice
- future approval action view
- future tool / agent activity panel

## 6.3 Tracking
Tracking must remain ahead of implementation and include:
- machine-readable Malone stage manifest
- current active Malone slice
- implementation order
- safety gates by stage
- dependencies between slices

---

## 7. Autonomous build readiness rules
To make Malone ready for autonomous build sequencing, every future slice must define:
- objective
- required inputs
- dependencies
- files likely touched
- safety gates
- validation tests
- rollout order
- rollback condition

This means every Malone phase should be representable in both human-readable markdown and machine-readable JSON.

---

## 8. Immediate next engineering slice
### Name
**Stage 1 — OpenAI Conversational Rendering with Deterministic Verification**

### Scope
- add backend OpenAI wrapper
- add render request schema
- generate truth packet from current deterministic result
- render verified conversational answer
- store render events in audit
- update Malone UI to display conversational answer + verified/fallback status

### Why this slice first
It dramatically improves user experience while preserving every core DSOS safety rule.

### Release rule
This slice is only complete when:
- key stays server-side
- render output is verifiably grounded
- fallback path works
- no schedule/auth regression occurs
- proposal persistence and prior audit flow remain intact

---

## 9. Success definition
Malone becomes world class not by being the most powerful first.
Malone becomes world class by being the most trustworthy while still becoming powerful.

The case-study value of DSOS will come from proving this sequence:

1. bounded AI
2. verified language enhancement
3. grounded retrieval
4. governed action proposals
5. approval-backed execution
6. tool orchestration
7. multi-agent operation
8. voice and local-model transition

That is the blueprint.
