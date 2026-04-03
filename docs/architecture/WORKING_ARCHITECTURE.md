# Working Architecture Snapshot

## Backend
- FastAPI
- SQLAlchemy
- JWT auth
- role-based dependency guards
- local runtime DB
- `/api/*` route namespace

## Frontend
- React
- Vite
- react-router-dom
- auth context
- protected route wrapper
- AllCare brand layer

## Core operational slice currently live
- auth
- scheduling
- basic workflows/events visibility
- role-aware controls

## Practical system flow
1. user logs in
2. JWT stored in localStorage
3. frontend sends bearer token to backend
4. backend resolves current user and role
5. write endpoints are role-guarded
6. scheduling slice performs create/list/cancel actions
7. frontend updates visible schedule feed

## Important implementation rules already learned
- do not use `metadata` as SQLAlchemy declarative field name
- use `meta_json` instead
- use valid email for seed login
- keep API and UI namespaces separate
- restart backend when model/auth files change
- restart frontend when route/auth shell files change significantly
