# Next thread prompt — read-only copilot JSON / telemetry (follow-on)

## Context

The DSOS Malone build now exposes **`malone_telemetry`** on `POST /api/malone/chat`, read-only **GET** routes under `/api/malone/inspect/`, and an optional **`MaloneInspectionPanel`** in `src/pages/MalonePage.jsx`. Scenario memory and decision traces are listable and fetchable by id with actor scoping.

## Suggested follow-ups (pick as needed)

1. **Pagination** for `/inspect/traces` (cursor or offset) when trace volume grows.  
2. **Role-based field redaction** on trace detail (e.g., hide `prompt_preview` for certain roles).  
3. **Correlation id** in `malone_telemetry` matching audit log rows (`log_malone_action`) for cross-system debugging.  
4. **Contract tests** (OpenAPI or snapshot) for `malone_telemetry` schema version 1.  
5. **E2E test** that opens the inspection panel and verifies read-only attributes (Playwright/Cypress if present).

## Constraints to preserve

- Single Malone path; no second copilot pipeline.  
- Telemetry must remain non-authoritative for answers.  
- No mutation API for traces or copilot JSON.  
- Current evidence and citations remain primary over scenario memory.

## Active lane

Work only under `app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/` — do not modify `backend/`, `frontend/`, or `dsos_replacements/`.
