We now have a working DSOS / AllCare Pharmacy system with:

- FastAPI backend
- React/Vite frontend
- JWT auth
- RBAC enforcement v1
- AllCare branding v1
- working schedule creation, viewing, and cancel flow
- `/api/*` backend route namespace
- protected frontend routes
- seeded working owner login:
  - owner@test.com
  - ChangeMe123!

We want to continue from the current working state.

Next objective:
Build department scoping + actor-aware audit tracking v1

Please:
1. audit the current architecture assumptions
2. design the cleanest production-grade next step
3. provide exact full-file replacements only
4. preserve current working auth, RBAC, schedule flow, and branding
5. update both backend and frontend where needed

Priority features:
- actor_user_id on all write actions
- department-aware filtering and scoping
- improved audit logging
- owner/admin operational visibility
- preserve working role model:
  - owner
  - admin
  - scheduler
  - viewer

Important constraints:
- no regressions to login flow
- no regressions to schedule create/list/cancel
- keep `/api/*` namespace
- keep `meta_json` usage instead of reserved SQLAlchemy `metadata`
- keep valid seed email:
  - owner@test.com

Ask for no unnecessary clarifications. Make best production-grade forward progress.
