# Malone Department Intake + Operations Mapping — Pass Report

## 1. WHY DEPARTMENT INTAKE + OPERATIONS MAPPING IS NEEDED

Organizations run on departments, workflows, tools, and handoffs. Without a structured way to capture that knowledge through the same Malone channel as policy and operations evidence, interviews stay in email or ad-hoc notes and cannot be governed, reviewed, or compared to source documents. This pass adds an **interaction layer** (sessions, answers, deterministic follow-ups) and a **structured map** (departments, roles, workflows, dependencies, handoffs, escalations, blockers, artifact references) that remain **auditable** and linked to **proposal + scenario memory** for traceability—without a second chatbot or a separate CRM.

## 2. CURRENT ORGANIZATIONAL-MEMORY LIMITATIONS

Previously, Malone could reason over scenario memory, operating copilot snapshots, and company knowledge review, but there was no first-class place to **run a department interview**, **track missing fields**, or **materialize** a normalized operations map from answers. Voice and text already share the Malone API stack; intake-specific storage and APIs were missing.

## 3. TARGET DEPARTMENT INTAKE ARCHITECTURE

- **Storage**: `department_intake_sessions` + `department_intake_answers` with `state_json` holding a versioned **profile** draft.
- **Audit link**: Each session creates a `MaloneProposal` (`department_intake`) and `MaloneScenarioMemory` (`scenario_type=department_intake`) plus a minimal `MaloneDecisionTrace` stub (inspectable, not legal-authoritative).
- **Follow-ups**: `compute_followup_questions` inspects missing profile fields and returns **deterministic** question objects (`reason`, `target_field`, `question_text`, `priority`).
- **Parsing**: `parse_intake_answer` applies lightweight keyword/keyed rules—no LLM interview loop in this pass.
- **API**: `/api/malone/operations-map/*` (same auth as Malone chat).
- **UI**: Minimal `DepartmentIntakePanel` on `MalonePage` using the same `fetch` + token pattern as other Malone calls.

## 4. TARGET OPERATIONS MAP MODEL

Normalized tables under `operations_departments` with children: roles, workflows, system tools, dependencies, handoffs, escalations, blockers, artifact refs (SOP names, etc.). Materialization **rebuilds** child rows from the latest intake profile for that department (explicit, reviewable). See `malone_operations_map_model.md`.

## 5. FOLLOW-UP QUESTIONING STRATEGY

Rules trigger when profile slices are empty or thin (mission, roles, workflows, systems, I/O, dependencies, handoffs, escalation, blockers, SOP refs). Output is sorted by priority and target field; fully inspectable JSON in session GET responses.

## 6. VOICE / TEXT INTAKE STRATEGY

Answers accept `entry_mode` of `text` or `voice_transcript`. Voice path reuses the same POST body as typing; optional `transcript_ref` is auto-generated for voice mode for linkage. Full voice UX can wrap transcripts from the existing listen flow without a separate engine.

## 7. SAFETY / GOVERNANCE MODEL

- Intake answers are **provisional**; `evidence_precedence_rank` keeps **legal/source-grounded** kinds above `intake_session_memory`.
- Map rows carry `from_intake` metadata; they do not override handbook or ingested policy text.
- Deterministic legal Malone behavior is unchanged (`handle_malone_request` untouched as an entrypoint).

## 8. WHAT THIS PASS IMPLEMENTED

- ORM models `app/models/operations_map.py` and Alembic `0009_department_intake_operations_map`.
- Services under `app/services/department_intake/` and `app/services/operations_map/`.
- API `app/api/operations_map_routes.py`; router registered in `app/main.py`.
- `schemas/operations_map_v0.sql` pointer.
- `DepartmentIntakePanel.jsx`, `maloneApi.js` helpers, `MalonePage.jsx` integration.
- Tests `tests/test_department_intake_operations_map.py`.

## 9. WHAT REMAINS DEFERRED

- Rich NLP parsing and entity resolution across departments.
- Automatic merge with org-chart HR systems.
- Deep integration attaching each answer line to ingestion control source versions.
- Full voice UX wiring from `VoiceInputButton` directly into intake POST (architecture supports transcript payloads).

## 10. HARD-FAIL COMPLIANCE CHECK

| Condition | Status |
|-----------|--------|
| No edits to `backend/`, `frontend/`, `dsos_replacements/` | Pass |
| Single Malone path (no parallel intake bot) | Pass |
| Intake not treated as automatic truth | Pass |
| Source-grounded precedence preserved | Pass |
| Legal citation-first path preserved | Pass |
| Tracking outputs present | Pass |
