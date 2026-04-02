# Pharmacy OS Auth + RBAC v1

This package contains production-grade replacement and new files to add Auth + RBAC v1
to the current DSOS backend and frontend.

## Backend files included
- app/models/models.py
- app/api/schemas.py
- app/services/auth_service.py
- app/api/auth_routes.py
- app/api/deps.py
- app/main.py
- requirements.txt

## Frontend files included
- src/lib/api.js
- src/context/AuthContext.jsx
- src/components/ProtectedRoute.jsx
- src/pages/LoginPage.jsx
- src/App.jsx
- src/main.jsx

## Install backend dependency
pip install pyjwt email-validator

## Default seeded login
owner@local.test
ChangeMe123!
