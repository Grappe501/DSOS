# Root Build Audit Report

**Root:** `H:\DSOS`
**Files scanned:** 262
**Total size:** 1.62 MB

## Executive Summary

- Frontend readiness: **100/100**
- Backend readiness: **70/100**
- Auth readiness: **20/100**
- Ingestion / AI readiness: **0/100**
- Tracking / handoff readiness: **100/100**

## Key Findings

- API route candidates found: **16**
- Tracking / handoff docs found: **50**
- Environment variable references found: **2**
- Duplicate filenames found: **31**
- Large files found: **0**
- Dead-zone candidates found: **10**
- Empty directories found: **1**

## package.json Summary

- Name: `pharmacy-os-frontend`
- Version: `0.1.0`
- Scripts:
  - `dev` → `vite`
  - `build` → `vite build`
  - `preview` → `vite preview`
- Runtime deps (3): react, react-dom, react-router-dom
- Dev deps (2): @vitejs/plugin-react, vite

## Directory Size Breakdown

- `runtime_v5.db`: 0.6 MB
- `tracking`: 0.43 MB
- `app`: 0.22 MB
- `tools`: 0.07 MB
- `dsos_replacements`: 0.07 MB
- `package-lock.json`: 0.05 MB
- `src`: 0.05 MB
- `dsos_file_replacements_v070_malone_persistence.txt`: 0.04 MB
- `test.db`: 0.02 MB
- `backend`: 0.02 MB
- `frontend`: 0.01 MB
- `docs`: 0.01 MB
- `spine`: 0.01 MB
- `scripts`: 0.0 MB
- `alembic`: 0.0 MB
- `schemas`: 0.0 MB
- `README_TEMPLATE_REGISTRY_ENGINE.md`: 0.0 MB
- `.env`: 0.0 MB
- `README.md`: 0.0 MB
- `README_TEMPLATE_ENGINE.md`: 0.0 MB

## File Extension Breakdown

- `.py`: 84
- `.md`: 73
- `.jsx`: 34
- `.tpl`: 27
- `.json`: 23
- `.js`: 7
- `.txt`: 4
- `[no_ext]`: 2
- `.db`: 2
- `.css`: 2
- `.example`: 1
- `.ini`: 1
- `.html`: 1
- `.sql`: 1

## Zone Breakdown

- `frontend`: 116
- `tracking_docs`: 55
- `other`: 54
- `tooling`: 24
- `backend`: 13

## API Routes / Backend Entry Candidates

- `api/contracts.md`
- `api/endpoints.md`
- `app/api/auth_routes.py`
- `app/api/deps.py`
- `app/api/malone_routes.py`
- `app/api/routes.py`
- `app/api/schemas.py`
- `backend/app/api/auth_routes.py`
- `backend/app/api/deps.py`
- `backend/app/api/routes.py`
- `backend/app/api/schemas.py`
- `dsos_replacements/app/api/routes.py`
- `dsos_replacements/app/api/schemas.py`
- `tools/templates/backend/api/deps.py.tpl`
- `tools/templates/backend/api/routes.py.tpl`
- `tools/templates/backend/api/schemas.py.tpl`

## Tracking / Handoff / Build Docs

- `HANDOFF_SUMMARY.txt`
- `app\services\audit_service.py`
- `app\services\workflows\engine_parts\audit.py`
- `backend\app\services\audit_service.py`
- `docs\spine\audit_logging.md`
- `dsos_replacements\app\services\audit_service.py`
- `dsos_replacements\src\pages\AuditPage.jsx`
- `frontend\src\pages\AuditPage.jsx`
- `spine\audit\audit.md`
- `spine\audit\audit_service.md`
- `src\pages\AuditPage.jsx`
- `tools\project_map_audit.py`
- `tools\root_mapper_audit.py`
- `tools\scaffold_size_audit.py`
- `tools\templates\backend\services\audit_service.py.tpl`
- `tools\templates\frontend\pages\AuditPage.jsx.tpl`
- `tracking\00_system_doctrine.md`
- `tracking\01_architecture_layers.md`
- `tracking\02_malone_agent_design.md`
- `tracking\03_self_improvement_loop.md`
- `tracking\04_voice_first_design.md`
- `tracking\05_ai_infrastructure.md`
- `tracking\06_building_blocks.md`
- `tracking\07_agent_replication.md`
- `tracking\08_phase4_direction.md`
- `tracking\CLEAN_SYSTEM_PROTOCOL.md`
- `tracking\HANDOFF_MIGRATION_MESSAGE.md`
- `tracking\NEW_THREAD_BOOT_SEQUENCE.md`
- `tracking\NEXT_PHASE_MASTER_BUILD_PLAN_v0.7.0.md`
- `tracking\NEXT_PHASE_MASTER_BUILD_PLAN_v0.8.0.md`
- `tracking\NEXT_THREAD_PROMPT.md`
- `tracking\PROJECT_MAP_AUDIT_README.md`
- `tracking\THREAD_MEMORY_COMPRESSION.md`
- `tracking\bootstrap_verification_report.json`
- `tracking\build_map.json`
- `tracking\current_state.json`
- `tracking\file_map_v0.7.0.json`
- `tracking\handoff_state_snapshot.json`
- `tracking\malone\MALONE_V1_MASTER_PLAN.md`
- `tracking\malone\malone_build_map.json`
- `tracking\malone\malone_build_sequence_v1.json`
- `tracking\malone\malone_manifest_v1.json`
- `tracking\manifest_rules_v0.7.0.json`
- `tracking\micro_steps.json`
- `tracking\phase_manifest_v0.7.0.json`
- `tracking\progress.json`
- `tracking\project_audit_report.json`
- `tracking\scaffold_size_audit_report.json`
- `tracking\scaffold_targets_v0.7.0.json`
- `tracking\update_progress_report.json`

## Documentation Files

- `HANDOFF_SUMMARY.txt`
- `README.md`
- `README_TEMPLATE_ENGINE.md`
- `README_TEMPLATE_REGISTRY_ENGINE.md`
- `api\contracts.md`
- `api\endpoints.md`
- `backend\requirements.txt`
- `docs\architecture\WORKING_ARCHITECTURE.md`
- `docs\core\overview.md`
- `docs\data\schema.md`
- `docs\git\GIT_SETUP_AND_RELEASE.md`
- `docs\modules\module_template.md`
- `docs\plan\NEXT_PHASE_PLAN.md`
- `docs\process\build_process.md`
- `docs\spine\ai_orchestration.md`
- `docs\spine\audit_logging.md`
- `docs\spine\auth_service.md`
- `docs\spine\event_bus.md`
- `docs\spine\forms_engine.md`
- `docs\spine\integration_gateway.md`
- `docs\spine\messaging_engine.md`
- `docs\spine\reminder_engine.md`
- `docs\spine\reporting_engine.md`
- `docs\spine\services.md`
- `docs\spine\task_engine.md`
- `docs\spine\workflow_engine.md`
- `docs\status\CURRENT_STATE.md`
- `docs\testing\SMOKE_TEST_CHECKLIST.md`
- `dsos_file_replacements_v070_malone_persistence.txt`
- `dsos_replacements\BUILD_NOTES.md`
- `events\event_registry.md`
- `flows\scheduling_flow.md`
- `requirements.txt`
- `runtime\runtime.md`
- `schemas\core_tables.md`
- `spine\ai\ai.md`
- `spine\ai\ai_service.md`
- `spine\audit\audit.md`
- `spine\audit\audit_service.md`
- `spine\auth\auth.md`
- `spine\auth\auth_service.md`
- `spine\event_bus\event_bus.md`
- `spine\event_bus\event_bus_service.md`
- `spine\forms\forms.md`
- `spine\forms\forms_service.md`
- `spine\integration\integration.md`
- `spine\integration\integration_service.md`
- `spine\messaging\messaging.md`
- `spine\messaging\messaging_service.md`
- `spine\reminder\reminder.md`
- `spine\reminder\reminder_service.md`
- `spine\reporting\reporting.md`
- `spine\reporting\reporting_service.md`
- `spine\task\task.md`
- `spine\task\task_service.md`
- `spine\workflow\workflow.md`
- `spine\workflow\workflow_service.md`
- `tests\testing_strategy.md`
- `tests\tests.md`
- `tracking\00_system_doctrine.md`
- `tracking\01_architecture_layers.md`
- `tracking\02_malone_agent_design.md`
- `tracking\03_self_improvement_loop.md`
- `tracking\04_voice_first_design.md`
- `tracking\05_ai_infrastructure.md`
- `tracking\06_building_blocks.md`
- `tracking\07_agent_replication.md`
- `tracking\08_phase4_direction.md`
- `tracking\CLEAN_SYSTEM_PROTOCOL.md`
- `tracking\HANDOFF_MIGRATION_MESSAGE.md`
- `tracking\NEW_THREAD_BOOT_SEQUENCE.md`
- `tracking\NEXT_PHASE_MASTER_BUILD_PLAN_v0.7.0.md`
- `tracking\NEXT_PHASE_MASTER_BUILD_PLAN_v0.8.0.md`
- `tracking\NEXT_THREAD_PROMPT.md`
- `tracking\PROJECT_MAP_AUDIT_README.md`
- `tracking\THREAD_MEMORY_COMPRESSION.md`
- `tracking\malone\MALONE_V1_MASTER_PLAN.md`

## Environment Variable References

- `OPENAI_API_KEY`
  - `app\services\openai_service.py`
- `VITE_API_BASE`
  - `dsos_replacements\src\lib\api.js`
  - `frontend\src\lib\api.js`

## Duplicate Filenames

- `App.jsx`
  - `dsos_replacements\src\App.jsx`
  - `frontend\src\App.jsx`
  - `src\App.jsx`
- `ApprovalsPage.jsx`
  - `frontend\src\pages\ApprovalsPage.jsx`
  - `src\pages\ApprovalsPage.jsx`
- `AuditPage.jsx`
  - `dsos_replacements\src\pages\AuditPage.jsx`
  - `frontend\src\pages\AuditPage.jsx`
  - `src\pages\AuditPage.jsx`
- `AuthContext.jsx`
  - `frontend\src\context\AuthContext.jsx`
  - `src\context\AuthContext.jsx`
- `DashboardPage.jsx`
  - `dsos_replacements\src\pages\DashboardPage.jsx`
  - `src\pages\DashboardPage.jsx`
- `DepartmentsPage.jsx`
  - `frontend\src\pages\DepartmentsPage.jsx`
  - `src\pages\DepartmentsPage.jsx`
- `LoginPage.jsx`
  - `frontend\src\pages\LoginPage.jsx`
  - `src\pages\LoginPage.jsx`
- `ProtectedRoute.jsx`
  - `frontend\src\components\ProtectedRoute.jsx`
  - `src\components\ProtectedRoute.jsx`
- `SchedulesPage.jsx`
  - `dsos_replacements\src\pages\SchedulesPage.jsx`
  - `src\pages\SchedulesPage.jsx`
- `__init__.py`
  - `app\services\workflows\__init__.py`
  - `app\services\workflows\engine_parts\__init__.py`
- `api.js`
  - `dsos_replacements\src\lib\api.js`
  - `frontend\src\lib\api.js`
  - `src\lib\api.js`
- `audit_service.py`
  - `app\services\audit_service.py`
  - `backend\app\services\audit_service.py`
  - `dsos_replacements\app\services\audit_service.py`
- `auth_routes.py`
  - `app\api\auth_routes.py`
  - `backend\app\api\auth_routes.py`
- `auth_service.md`
  - `docs\spine\auth_service.md`
  - `spine\auth\auth_service.md`
- `auth_service.py`
  - `app\services\auth_service.py`
  - `backend\app\services\auth_service.py`
- `department_service.py`
  - `app\services\department_service.py`
  - `backend\app\services\department_service.py`
- `deps.py`
  - `app\api\deps.py`
  - `backend\app\api\deps.py`
- `event_bus.md`
  - `docs\spine\event_bus.md`
  - `spine\event_bus\event_bus.md`
- `events.json`
  - `events\events.json`
  - `registry\events.json`
- `main.jsx`
  - `frontend\src\main.jsx`
  - `src\main.jsx`
- `main.py`
  - `app\main.py`
  - `backend\app\main.py`
  - `dsos_replacements\app\main.py`
- `messaging_service.py`
  - `app\services\messaging_service.py`
  - `dsos_replacements\app\services\messaging_service.py`
- `models.py`
  - `app\models\models.py`
  - `backend\app\models\models.py`
- `requirements.txt`
  - `requirements.txt`
  - `backend\requirements.txt`
- `routes.py`
  - `app\api\routes.py`
  - `backend\app\api\routes.py`
  - `dsos_replacements\app\api\routes.py`
- `schedule_service.py`
  - `app\services\schedule_service.py`
  - `backend\app\services\schedule_service.py`
  - `dsos_replacements\app\services\schedule_service.py`
- `schemas.py`
  - `app\api\schemas.py`
  - `backend\app\api\schemas.py`
  - `dsos_replacements\app\api\schemas.py`
- `session.py`
  - `app\db\session.py`
  - `dsos_replacements\app\db\session.py`
- `styles.css`
  - `dsos_replacements\src\styles.css`
  - `src\styles.css`
- `task_service.py`
  - `app\services\task_service.py`
  - `dsos_replacements\app\services\task_service.py`
- `workflow_service.py`
  - `app\services\workflow_service.py`
  - `backend\app\services\workflow_service.py`
  - `dsos_replacements\app\services\workflow_service.py`

## Dead-Zone / Stub Candidates

- `app\services\workflows\__init__.py` — tiny source file (lines=2, bytes=47)
- `app\services\workflows\engine_parts\__init__.py` — tiny source file (lines=2, bytes=37)
- `backend\app\api\routes.py` — tiny source file (lines=0, bytes=0)
- `backend\app\services\audit_service.py` — tiny source file (lines=0, bytes=0)
- `backend\app\services\department_service.py` — tiny source file (lines=0, bytes=0)
- `backend\app\services\schedule_service.py` — tiny source file (lines=0, bytes=0)
- `backend\app\services\workflow_service.py` — tiny source file (lines=0, bytes=0)
- `frontend\src\pages\ApprovalsPage.jsx` — tiny source file (lines=0, bytes=0)
- `frontend\src\pages\AuditPage.jsx` — tiny source file (lines=0, bytes=0)
- `frontend\src\pages\DepartmentsPage.jsx` — tiny source file (lines=0, bytes=0)

## Empty Directories

- `tracking\reports`

## Signal Counts

- `ai`: 28
- `auth`: 35
- `backend`: 77
- `database`: 13
- `frontend`: 43
- `ingestion`: 26
- `tracking`: 70

## Build Direction Recommendations

- Create a dedicated ingestion pipeline module before building the regulation Q&A layer.

## Suggested Next Build Modules

- `ingestion/` — handbook parsing, chunking, normalization, metadata enrichment
- `knowledge/` — source registry, citation store, handbook versions
- `retrieval/` — embeddings, vector search, lexical fallback, reranking
- `assistant/` — answer orchestration, citation formatting, guardrails
- `compliance/` — source trust scoring, effective-date validation, policy versioning
- `tracking/` — deterministic build state, upgrade logs, next-thread protocol
