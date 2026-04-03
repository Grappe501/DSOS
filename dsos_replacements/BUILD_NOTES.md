# DSOS / AllCare Pharmacy — Department Scoping + Actor Audit v1

## What this replacement pack does
- Preserves the working JWT auth, RBAC, branding, and schedule flow.
- Adds actor-aware audit capture to schedule, task, message, and workflow write paths.
- Adds department-aware schedule scoping.
- Adds owner/admin operational visibility with a new audit screen and operational summary endpoint.
- Adds lightweight runtime schema repair for older SQLite local databases.

## Architecture assumptions confirmed
1. `app/` and `src/` are the active backend/frontend roots.
2. `backend/app` and `frontend/src` appear to be older shadow copies and should not be treated as the live source of truth unless your local run scripts explicitly point there.
3. The runtime is still SQLite + `Base.metadata.create_all()` without Alembic. Because of that, schema changes must be repaired explicitly for existing local databases.
4. The role model is preserved exactly:
   - owner
   - admin
   - scheduler
   - viewer
5. Production scoping rules implemented here:
   - owner/admin: global visibility
   - scheduler/viewer: department-scoped visibility
   - scheduler writes are locked to their own department

## Step-by-step build forward
1. Replace the files in this pack into the project root.
2. Restart the FastAPI backend so the runtime schema repair runs.
3. Restart the Vite frontend.
4. Log in with `owner@test.com` / `ChangeMe123!`.
5. Smoke test:
   - login
   - schedules load
   - create a schedule with a department
   - cancel a schedule
   - open Dashboard and confirm scoped metrics
   - open Audit and confirm `actor_user_id`, `actor_role`, `actor_department`, and `department`
6. After that, the next production move should be:
   - add a real departments table
   - add user management UI
   - migrate from bootstrap schema repair to Alembic migrations
   - add actor-aware audit for every remaining write slice
   - add row-level scoping for workflows/messages/reminders if those become department-owned records

## Validation I completed here
- Python syntax compile passed for all replaced backend files.
- I could not fully run the backend in this container because required Python packages are not installed here.
- I could not complete a Vite production build because the bundled `node_modules` in the zip are missing a Rollup optional native dependency for this Linux container.
