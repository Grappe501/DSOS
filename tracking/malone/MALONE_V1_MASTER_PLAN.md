
# Malone v1 Master Build Plan

## Objective
Build Malone v1 as a bounded AI orchestration layer on top of the deterministic core.

## Core Principle
AI proposes. Deterministic core validates. Nothing bypasses validation.

---

## System Pipeline
Input → Intent → Plan → Simulation → Validation → Proposal → Approval → Execution → Audit

---

## Phase Breakdown

### Phase A: Foundation
- Malone service (backend)
- Intent parsing
- Prompt registry
- OpenAI integration (env-based)

### Phase B: Core Capabilities
- Answer mode
- Analyst mode
- Proposal system
- Audit logging for Malone

### Phase C: Agent System
- Agent service
- ReportAgent (first agent)
- Agent run tracking

### Phase D: Frontend
- Malone page
- Chat panel
- Proposal panel
- Agent activity panel

### Phase E: Governance
- Proposal approval flow
- Role-based execution
- Department scoping enforcement

---

## Deliverables
- Backend services
- API routes
- Frontend UI
- Proposal + AgentRun models
- Tracking integration
