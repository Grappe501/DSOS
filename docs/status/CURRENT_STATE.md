# Current Working State

## Confirmed working
### Backend
- `app/main.py` starts
- auth router is mounted
- api router is mounted
- root router is mounted
- CORS is configured for Vite local dev
- `Role` and `User` models exist
- `WorkflowState.meta_json` is used instead of reserved `metadata`
- `AuditLog.meta_json` is used instead of reserved `metadata`
- seed auth user is valid:
  - `owner@test.com`
  - `ChangeMe123!`

### Frontend
- login screen works
- auth context works
- protected routes work
- branded shell works
- AllCare styling pass v1 works
- schedules page works
- create schedule works
- list schedules works
- cancel schedule works

## Confirmed architectural milestones
1. runtime foundation
2. API/UI split
3. auth + JWT session layer
4. RBAC enforcement v1
5. brand pass v1
6. working scheduling slice

## Current role model
- owner: full access
- admin: operational access
- scheduler: schedule write access
- viewer: read-only

## Current known constraints
- git may not yet be initialized in local folder
- actor-aware auditing is not complete
- department scoping is not complete
- admin/user management UI is not built yet
- message center UI is not built yet
- recurring schedule management UI is incomplete
- conflict resolution UI is incomplete

## Current likely critical files
### Backend
- `app/main.py`
- `app/api/routes.py`
- `app/api/auth_routes.py`
- `app/api/deps.py`
- `app/api/schemas.py`
- `app/services/auth_service.py`
- `app/models/models.py`
- `app/services/schedule_service.py`
- `app/services/workflow_service.py`
- `app/services/audit_service.py`
- `app/services/messaging_service.py`

### Frontend
- `src/main.jsx`
- `src/App.jsx`
- `src/lib/api.js`
- `src/context/AuthContext.jsx`
- `src/components/ProtectedRoute.jsx`
- `src/pages/LoginPage.jsx`
- `src/pages/SchedulesPage.jsx`
- `src/styles.css`
