# DSOS / AllCare Pharmacy  
## Next Phase Master Build Plan  
### v0.7.0 — Department Operations + Approval Workflow

**Purpose**  
This document is the master implementation blueprint for the next production phase after the currently working system state. It is designed to live in the `tracking/` folder as the source-of-truth map for engineering, handoff, and future automation scaffolding.

**Source-of-truth status**  
The current tracking data shows:
- current phase: `phase_3_department_audit`
- active module: `department_scoping_and_actor_audit`
- current task: `design_and_apply_production_grade_replacements`
- last working version: `v0.6.1-auth-rbac-branding`
- completed milestones: runtime foundation, API/UI split, auth, RBAC v1, branding v1, working schedule flow
- immediate next priorities: department scoping, actor-aware audit tracking, owner/admin operational visibility

This aligns with the existing tracking structure and progress metadata already present in the repository.

---

## 1. Why this document exists

This file does three jobs at once:

1. **Master build plan**  
   It defines exactly what the next implementation phase is.

2. **Precise file map**  
   It identifies the backend and frontend files that will be created, updated, or left untouched.

3. **Automation preparation map**  
   It is the first intentional step toward generating future build phases with Python scaffolding scripts instead of manually rebuilding the plan from scratch every time.

The next action after this plan is **not** to jump blindly into code.  
The next action is to create a **Python scaffolding script** that can:
- read the current tracking state,
- read or generate the next phase map,
- create folders and placeholder files,
- write machine-readable tracking updates,
- and prepare deterministic implementation steps for the next build.

---

## 2. Current known repository / handoff structure

The current repository structure from the tracking map is:

```text
.
├── README.md
├── NEXT_THREAD_PROMPT.md
├── docs/
│   ├── status/
│   │   └── CURRENT_STATE.md
│   ├── plan/
│   │   └── NEXT_PHASE_PLAN.md
│   ├── architecture/
│   │   └── WORKING_ARCHITECTURE.md
│   ├── git/
│   │   └── GIT_SETUP_AND_RELEASE.md
│   └── testing/
│       └── SMOKE_TEST_CHECKLIST.md
└── tracking/
    ├── current_state.json
    ├── micro_steps.json
    ├── progress.json
    └── build_map.json
```

The current application codebase is assumed to be rooted at:

```text
backend/app/
frontend/src/
```

If the live working code instead uses:
```text
app/
src/
```
then the scaffold layer should be able to support both layouts by configuration. That is one of the reasons the scaffold system is the next important step.

---

## 3. Current working application baseline

The current DSOS / AllCare Pharmacy system is working with:

- FastAPI backend
- React/Vite frontend
- JWT authentication
- RBAC enforcement v1
- AllCare branding v1
- working schedule creation and viewing

The current version is **before**:
- formal department scoping
- actor-aware audit tracking across all write actions
- owner/admin operational visibility
- approval workflow
- formal department membership
- migration discipline for complex schema evolution

That means the current system is stable enough to extend, but not yet deep enough to be considered operationally mature.

---

## 4. Phase naming and strategic objective

## Phase name
**v0.7.0 — Department Operations + Approval Workflow**

## Strategic objective
Evolve the system from a working authenticated schedule app into a department-aware operational system with traceable writes, approval workflow, and admin-grade visibility.

## Required outcome
By the end of v0.7.0, the application should support:

- formal department membership
- department-aware filtering and enforcement
- actor-aware audit logging on write paths
- richer audit review capability
- schedule status workflow
- approval and rejection actions
- owner/admin operations dashboard
- scoped visibility by department
- migration-safe schema evolution

---

## 5. Design principles for this phase

These principles should govern the build:

### 5.1 Preserve what is already working
Do not break:
- auth
- JWT handling
- protected routes
- RBAC v1
- existing schedule create/list/cancel flow unless intentionally upgraded
- current branding shell

### 5.2 Add scope without collapsing simplicity
The next layer should not overcomplicate the codebase.  
Authorization should remain understandable:

- **role** = what class of actions is possible
- **department scope** = where those actions are allowed
- **workflow state** = whether the action is operationally valid
- **audit** = who did what, where, and when

### 5.3 Build toward automation
Every phase from here forward should be mapped in a way that a Python script can scaffold:
- directories
- file placeholders
- tracking files
- micro-step expansions
- implementation checklists
- release state handoff artifacts

### 5.4 Make the map more detailed than the current code
The plan should always be ahead of the implementation.

---

## 6. What comes immediately before coding

The next engineering step after placing this file in `tracking/` is:

## Build the scaffolding generator script

This script should become the beginning of the automation layer for future phases.

### Proposed location
```text
tools/scaffold_next_phase.py
```

### Initial purpose
Given a phase definition, the script should:
- read `tracking/current_state.json`
- read `tracking/progress.json`
- read `tracking/build_map.json`
- read `tracking/micro_steps.json`
- create missing planning folders/files
- write new master build plan files for upcoming phases
- generate placeholder backend/frontend file trees
- produce machine-readable scaffold output for handoff

### Why this matters
This moves the build from “manual planning and manual file assembly” to:
- deterministic phase generation
- repeatable engineering setup
- future partial code generation
- build-state continuity across threads

This is the first real step toward a self-mapping and eventually partially self-scaffolding build system.

---

## 7. v0.7.0 implementation scope

### 7.1 Department scoping v2
The current system likely uses a simple department string on the user or schedule model.  
That is not enough for long-term operational control.

v0.7.0 introduces:
- canonical departments
- user department membership
- primary department designation
- cross-department assignment support
- scoped read/write enforcement

### 7.2 Actor-aware audit tracking v2
Every write action must capture:
- who performed it
- which role they had
- which department it touched
- what entity changed
- what changed before and after
- when it happened
- request correlation context

### 7.3 Schedule approval workflow
Schedules should become lifecycle-managed instead of simple records.

Target statuses:
- `draft`
- `submitted`
- `approved`
- `rejected`
- `scheduled`
- `cancelled`

### 7.4 Owner/Admin operational visibility
Operational users need:
- summary dashboard
- pending approvals
- department-filtered activity
- audit review
- schedule counts by status and scope

---

## 8. Target backend architecture

## 8.1 Backend root
Assumed root:
```text
backend/app/
```

## 8.2 Backend target file map

### Existing files likely to update
```text
backend/app/main.py
backend/app/api/routes.py
backend/app/api/deps.py
backend/app/api/schemas.py
backend/app/db/session.py
backend/app/models/models.py
backend/app/services/auth_service.py
backend/app/services/audit_service.py
backend/app/services/schedule_service.py
backend/app/services/workflow_service.py
backend/app/services/task_service.py
backend/app/services/messaging_service.py
```

### New backend files to create
```text
backend/app/services/department_service.py
backend/app/services/ops_service.py
backend/app/models/department.py              # optional if model split begins now
backend/app/models/membership.py              # optional if model split begins now
```

### Migration layer to create
```text
backend/alembic.ini
backend/alembic/env.py
backend/alembic/versions/
backend/alembic/versions/<revision>_v070_department_workflow.py
```

### New backend test files recommended
```text
backend/tests/test_department_scope.py
backend/tests/test_audit_logging.py
backend/tests/test_schedule_workflow.py
backend/tests/test_operational_summary.py
```

---

## 9. Target frontend architecture

## 9.1 Frontend root
Assumed root:
```text
frontend/src/
```

## 9.2 Frontend target file map

### Existing files likely to update
```text
frontend/src/App.jsx
frontend/src/main.jsx
frontend/src/lib/api.js
frontend/src/context/AuthContext.jsx
frontend/src/pages/DashboardPage.jsx
frontend/src/pages/SchedulesPage.jsx
frontend/src/styles.css
```

### New frontend pages to create
```text
frontend/src/pages/AuditPage.jsx
frontend/src/pages/ApprovalsPage.jsx
frontend/src/pages/DepartmentsPage.jsx
```

### New frontend shared components recommended
```text
frontend/src/components/FilterBar.jsx
frontend/src/components/StatusPill.jsx
frontend/src/components/ScopeBadge.jsx
frontend/src/components/TableEmptyState.jsx
frontend/src/components/DepartmentSelect.jsx
```

### Frontend files likely unchanged in v0.7.0
```text
frontend/src/pages/LoginPage.jsx
frontend/src/pages/CalendarPage.jsx
frontend/src/pages/EventsPage.jsx
frontend/src/pages/MessagesPage.jsx
frontend/src/pages/WorkflowsPage.jsx
frontend/src/components/ProtectedRoute.jsx
frontend/src/components/PageHeader.jsx
frontend/src/components/DataState.jsx
frontend/src/components/StatCard.jsx
```

---

## 10. Backend model blueprint

## 10.1 Department model

### Recommended file location
If models remain centralized:
```text
backend/app/models/models.py
```

If models are split:
```text
backend/app/models/department.py
```

### Fields
- `id`
- `code`
- `name`
- `description`
- `is_active`
- `created_at`
- `updated_at`

### Notes
This becomes the canonical department registry.  
Do not rely forever on free-text department strings.

---

## 10.2 UserDepartmentMembership model

### Recommended location
If centralized:
```text
backend/app/models/models.py
```

If split:
```text
backend/app/models/membership.py
```

### Fields
- `id`
- `user_id`
- `department_id`
- `is_primary`
- `can_approve`
- `is_active`
- `created_at`
- `updated_at`

### Notes
This is the operational scoping layer that sits under RBAC.

---

## 10.3 Schedule model expansion

### File location
```text
backend/app/models/models.py
```

### Fields to add
- `department_id`
- `status`
- `submitted_by_user_id`
- `submitted_at`
- `approved_by_user_id`
- `approved_at`
- `rejected_by_user_id`
- `rejected_at`
- `rejection_reason`
- `cancelled_by_user_id`
- `cancelled_at`

### Notes
Do not remove the current working schedule flow.  
Evolve it carefully.

---

## 10.4 AuditLog model expansion

### File location
```text
backend/app/models/models.py
```

### Required fields
- `actor_user_id`
- `action`
- `entity_type`
- `entity_id`
- `department`
- `request_id`
- `before_json`
- `after_json`
- `meta_json`
- `created_at`

### Notes
This is the minimum operational audit foundation.

---

## 11. Backend API and service blueprint

## 11.1 Dependency and scope resolution

### File
```text
backend/app/api/deps.py
```

### Responsibilities
- resolve current user from JWT
- resolve user role
- resolve department scope
- determine whether user is global or scoped
- expose helper checks used by routes/services

---

## 11.2 Department service

### File
```text
backend/app/services/department_service.py
```

### Responsibilities
- list departments
- create departments
- assign memberships
- return allowed departments for a user
- check whether user can operate in a department
- check whether user can approve in a department

---

## 11.3 Audit service

### File
```text
backend/app/services/audit_service.py
```

### Responsibilities
- normalize audit event creation
- capture actor context
- capture before/after snapshots
- attach request_id
- store scoped metadata
- expose filtered audit query methods

### Required helper functions
- `build_request_id()`
- `serialize_snapshot()`
- `log_write_action(...)`
- `log_transition(...)`
- `list_audit_events(...)`

---

## 11.4 Schedule service

### File
```text
backend/app/services/schedule_service.py
```

### Responsibilities
- create schedule draft
- submit schedule
- approve schedule
- reject schedule
- cancel schedule
- list schedules by scope
- validate workflow transitions
- call audit service for all write actions

---

## 11.5 Workflow service

### File
```text
backend/app/services/workflow_service.py
```

### Responsibilities
- write transition records
- return workflow history
- ensure schedule state transitions are tracked consistently

---

## 11.6 Ops service

### File
```text
backend/app/services/ops_service.py
```

### Responsibilities
- compute operational summary cards
- get pending approvals
- get recent activity
- aggregate status counts by department and role scope

---

## 11.7 Route additions

### File
```text
backend/app/api/routes.py
```

### New endpoints
```text
GET    /api/departments
POST   /api/departments
GET    /api/users/{user_id}/departments
PUT    /api/users/{user_id}/departments

POST   /api/schedules/create
PATCH  /api/schedules/{schedule_id}
POST   /api/schedules/{schedule_id}/submit
POST   /api/schedules/{schedule_id}/approve
POST   /api/schedules/{schedule_id}/reject
POST   /api/schedules/{schedule_id}/cancel

GET    /api/audit
GET    /api/operational/summary
GET    /api/operational/pending-approvals
GET    /api/operational/activity
```

### Route goals
- preserve current auth and schedule routes
- add new workflow routes without breaking the existing UX
- keep all routes actor-aware and scope-aware

---

## 12. Frontend page blueprint

## 12.1 DashboardPage.jsx
### File
```text
frontend/src/pages/DashboardPage.jsx
```

### Add
- total schedules in scope
- pending approvals
- approved today
- cancelled today
- recent audit activity
- department filter for owner/admin
- scoped summaries for limited users

---

## 12.2 SchedulesPage.jsx
### File
```text
frontend/src/pages/SchedulesPage.jsx
```

### Add
- status column
- department column
- department filter
- submit button
- approve/reject controls when authorized
- rejection reason display
- status filters

### Preserve
- current list/create/cancel flow

---

## 12.3 AuditPage.jsx
### File
```text
frontend/src/pages/AuditPage.jsx
```

### Purpose
Provide owner/admin operational review of write activity.

### Features
- action filter
- entity type filter
- actor filter
- department filter
- date range filter
- request_id filter
- event detail modal or expandable rows

---

## 12.4 ApprovalsPage.jsx
### File
```text
frontend/src/pages/ApprovalsPage.jsx
```

### Purpose
Single queue for schedules awaiting approval.

### Features
- pending list
- approve action
- reject action
- optional notes field
- department filter for owner/admin

---

## 12.5 DepartmentsPage.jsx
### File
```text
frontend/src/pages/DepartmentsPage.jsx
```

### Purpose
Allow owner/admin to see and manage department structure.

### Features
- department list
- create department
- view user memberships
- assign membership
- primary department display

---

## 13. Migration blueprint

## 13.1 Required migration layer
Add Alembic now.

### Files
```text
backend/alembic.ini
backend/alembic/env.py
backend/alembic/versions/<revision>_v070_department_workflow.py
```

### First migration responsibilities
- create `departments`
- create `user_department_memberships`
- alter `schedules`
- alter `audit_logs`
- backfill distinct departments from existing data
- backfill memberships from user department fields
- map schedules to canonical departments

### Reason
This is the point where ad hoc schema patching becomes too risky.

---

## 14. Testing blueprint

## 14.1 Backend smoke tests
Create or update:

```text
backend/tests/test_department_scope.py
backend/tests/test_audit_logging.py
backend/tests/test_schedule_workflow.py
backend/tests/test_operational_summary.py
```

### Must verify
- login still works
- current auth middleware still works
- current schedule list still works
- scheduler sees only allowed departments
- viewer is read-only
- owner sees everything
- scoped admin sees only allowed departments
- submit/approve/reject/cancel transitions work
- audit rows capture actor and before/after state

## 14.2 Frontend smoke checks
Document in:
```text
docs/testing/SMOKE_TEST_CHECKLIST.md
```

### Must verify
- login unchanged
- dashboard renders by role
- schedules page renders by scope
- audit page loads for authorized users
- approvals page works
- departments page works
- old flow does not regress

---

## 15. Tracking system updates required for this phase

The `tracking/` folder must expand, not stay flat forever.

## Current files
```text
tracking/current_state.json
tracking/micro_steps.json
tracking/progress.json
tracking/build_map.json
```

## Recommended additions for stronger phase mapping
```text
tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.7.0.md
tracking/file_map_v0.7.0.json
tracking/phase_manifest_v0.7.0.json
tracking/scaffold_targets_v0.7.0.json
tracking/automation_notes.md
tracking/release_targets.json
```

### Why these matter
- `file_map_v0.7.0.json` gives a machine-readable version of this document
- `phase_manifest_v0.7.0.json` gives explicit phase metadata
- `scaffold_targets_v0.7.0.json` tells the Python script what to generate
- `automation_notes.md` records assumptions and automation strategy
- `release_targets.json` tracks version/state transitions

---

## 16. Recommended machine-readable scaffold formats

## 16.1 file_map_v0.7.0.json
Should contain:
- backend create list
- backend update list
- frontend create list
- frontend update list
- migration files
- test files
- docs files

## 16.2 phase_manifest_v0.7.0.json
Should contain:
- phase name
- version
- objective
- dependencies
- required endpoints
- required models
- required UI pages
- test targets
- completion criteria

## 16.3 scaffold_targets_v0.7.0.json
Should contain:
- directories to create
- files to touch
- placeholders to write
- templates to use
- tracking files to update

---

## 17. Python scaffolding script blueprint

## Proposed first scaffold script
```text
tools/scaffold_next_phase.py
```

## Supporting templates folder
```text
tools/templates/
```

## Optional future split
```text
tools/templates/markdown/
tools/templates/json/
tools/templates/backend/
tools/templates/frontend/
```

## Minimum first version behavior
The first version of the script should:

1. detect the repository layout
2. read the tracking JSON files
3. create missing `tracking/` phase artifacts
4. create missing `docs/` support files
5. generate machine-readable file maps
6. create placeholder files for new backend/frontend components
7. update progress metadata for the next phase scaffold
8. generate a scaffold report

## Recommended output files from the script
```text
tracking/file_map_v0.7.0.json
tracking/phase_manifest_v0.7.0.json
tracking/scaffold_targets_v0.7.0.json
tracking/scaffold_report_v0.7.0.md
```

## Recommended later capabilities
After the initial scaffold pass, later versions of the script should be able to:
- generate route stubs
- generate service stubs
- generate schema stubs
- generate test skeletons
- generate release note files
- generate handoff prompt updates
- eventually compose partial code using templates

---

## 18. Micro-step engineering plan for v0.7.0

This should become the expanded step ladder in tracking.

### Step group A — migration setup
1. add Alembic
2. create first migration
3. backfill departments and memberships
4. verify old data survives

### Step group B — backend models
5. add Department model
6. add UserDepartmentMembership model
7. expand Schedule model
8. expand AuditLog model

### Step group C — backend services
9. build department service
10. normalize audit service
11. update schedule service for workflow transitions
12. add ops aggregation service

### Step group D — backend routes
13. add departments routes
14. add schedule workflow routes
15. add audit filtering route
16. add operational summary routes

### Step group E — frontend
17. add AuditPage
18. add ApprovalsPage
19. add DepartmentsPage
20. update DashboardPage
21. update SchedulesPage
22. update App routing and nav

### Step group F — testing and release
23. run backend tests
24. run frontend smoke tests
25. update docs
26. update tracking files
27. tag release candidate
28. tag final version

---

## 19. Definition of done

v0.7.0 is complete when all of the following are true:

- departments are canonicalized
- user memberships are formalized
- schedule actions are department-aware
- write actions are actor-aware
- audit data captures before/after state
- approval routes work
- owner/admin summary views work
- frontend exposes audit/approvals/departments pages
- migrations exist and are used
- current auth and schedule baseline still works
- tracking artifacts are updated for handoff

---

## 20. Exact explicit file map

## 20.1 Backend — create
```text
backend/app/services/department_service.py
backend/app/services/ops_service.py
backend/alembic.ini
backend/alembic/env.py
backend/alembic/versions/<revision>_v070_department_workflow.py
backend/tests/test_department_scope.py
backend/tests/test_audit_logging.py
backend/tests/test_schedule_workflow.py
backend/tests/test_operational_summary.py
```

## 20.2 Backend — update
```text
backend/app/main.py
backend/app/api/routes.py
backend/app/api/deps.py
backend/app/api/schemas.py
backend/app/db/session.py
backend/app/models/models.py
backend/app/services/auth_service.py
backend/app/services/audit_service.py
backend/app/services/schedule_service.py
backend/app/services/workflow_service.py
backend/app/services/task_service.py
backend/app/services/messaging_service.py
```

## 20.3 Frontend — create
```text
frontend/src/pages/AuditPage.jsx
frontend/src/pages/ApprovalsPage.jsx
frontend/src/pages/DepartmentsPage.jsx
frontend/src/components/FilterBar.jsx
frontend/src/components/StatusPill.jsx
frontend/src/components/ScopeBadge.jsx
frontend/src/components/TableEmptyState.jsx
frontend/src/components/DepartmentSelect.jsx
```

## 20.4 Frontend — update
```text
frontend/src/App.jsx
frontend/src/main.jsx
frontend/src/lib/api.js
frontend/src/context/AuthContext.jsx
frontend/src/pages/DashboardPage.jsx
frontend/src/pages/SchedulesPage.jsx
frontend/src/styles.css
```

## 20.5 Tracking — create
```text
tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.7.0.md
tracking/file_map_v0.7.0.json
tracking/phase_manifest_v0.7.0.json
tracking/scaffold_targets_v0.7.0.json
tracking/automation_notes.md
tracking/release_targets.json
```

## 20.6 Tools — create
```text
tools/scaffold_next_phase.py
tools/templates/
tools/templates/markdown/
tools/templates/json/
tools/templates/backend/
tools/templates/frontend/
```

---

## 21. Explicit next action after this document

After this markdown file is placed in the `tracking/` folder, the next action is:

## Build `tools/scaffold_next_phase.py`

That script should:
- read current tracking files
- generate the new machine-readable phase files
- create the next planned directories and placeholder files
- prepare the repository for v0.7.0 implementation
- become the first reusable automation layer for future DSOS phases

This is the correct next step because it expands the map first, which later makes partial automation and deterministic build generation possible.

---

## 22. Recommended follow-up artifacts after this file

Immediately after this file, generate:

1. `tracking/file_map_v0.7.0.json`
2. `tracking/phase_manifest_v0.7.0.json`
3. `tracking/scaffold_targets_v0.7.0.json`
4. `tools/scaffold_next_phase.py`

Those four artifacts together become the first real bridge between:
- planning
- implementation
- automation
- handoff continuity

---

## 23. Final instruction for future threads

When a future thread picks up from here, it should treat this document as the authoritative next-phase build map.

The next thread should:
1. read this file first
2. generate the machine-readable scaffold files
3. build the Python scaffold script
4. scaffold the v0.7.0 phase structure
5. only then begin full implementation

That order matters because the goal is no longer just to build the product.  
The goal is to build the **map that can increasingly help build the product**.

---
