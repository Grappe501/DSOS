# Malone read-only copilot JSON and telemetry — pass report

## 1. WHY READ-ONLY COPILOT JSON / TELEMETRY IS NEEDED

Structured operating copilot blocks, decision workflow snapshots, and persisted scenario/decision traces are essential for governance, debugging, and tuning. Without a **stable, read-only** surface, operators must scrape large `truth_packet` blobs or database rows ad hoc, which is error-prone and mixes observational metadata with authoritative answers. Lightweight **turn telemetry** (route, pattern, fallbacks, evidence scope, deterministic mode, prior-analog counts) makes it possible to compare runs, audit routing, and validate precedence rules without introducing a second Malone path or mutating stored state.

## 2. CURRENT OPERATING COPILOT / TRACE INSPECTION LIMITATIONS

Before this pass, the chat response already carried a full `truth_packet` (including `operating_copilot` and `decision_workflow` when enabled), but there was **no compact, versioned telemetry object** for clients or scripts. Persisted scenario memory and decision traces existed in the database, but **no narrow HTTP API** exposed them for authenticated inspection; developers relied on direct DB access or internal helpers. The UI did not offer an optional, clearly read-only inspection affordance tied to the same Malone response.

## 3. TARGET READ-ONLY EXPOSURE ARCHITECTURE

- **Single Malone path**: `handle_malone_request` remains the only chat entry; telemetry is appended as **`malone_telemetry`** on the same JSON response (pure summary; answers unchanged).
- **Truth packet unchanged in authority**: Full `truth_packet` continues to hold `operating_copilot`, `decision_workflow`, and evidence; telemetry duplicates **summaries and pointers** only.
- **Read-only HTTP**: Authenticated **GET** routes under `/api/malone/inspect/` return schema description, recent traces, and trace detail. No POST/PATCH/DELETE for copilot or trace data.
- **Optional UI**: A collapsible **MaloneInspectionPanel** shows `malone_telemetry` and optional subsets of `truth_packet` in read-only textareas, plus a button to fetch persisted trace JSON via the inspect API.

## 4. TELEMETRY MODEL

`malone_telemetry` (schema version **1**) includes: `read_only`, `precedence_note` (from `PRECEDENCE_NOTE`), intent target/mode, `scenario_route` (primary scenario + router payload), summarized `operating_copilot` / `decision_workflow`, `answer_pattern` (pattern id + packet_meta labels), `fallbacks`, `evidence_scope`, `cross_source` (evidence-scope vs legal cross-source policy gate), `delivery` (`delivery_mode`, deterministic legal mode bucket, `verified`), `scenario_memory` (prior analog count, optional emit flag), `trace_ids`, and relative `inspect_routes`. It is built **after** the turn by `build_turn_telemetry` and **does not** feed back into generation.

## 5. TRACE ACCESS STRATEGY

- **List**: `GET /api/malone/inspect/traces` returns recent `malone_scenario_memories` rows, ordered by `created_at`, **scoped to the current user** unless role is `owner` or `admin`.
- **Detail**: `GET /api/malone/inspect/traces/{scenario_memory_id}` returns `serialize_readonly_trace_bundle`: scenario row metadata plus the linked `malone_decision_traces` row with JSON fields parsed; large JSON may be truncated with `_truncated` previews.
- **Authorization**: `can_read_scenario` enforces owner/admin or matching `actor_user_id`.

## 6. SAFETY / PRECEDENCE MODEL

1. **Current source-grounded evidence outranks prior scenario memory** — unchanged; telemetry repeats `precedence_note` for visibility only.
2. **Telemetry and trace inspection do not alter answers** — computed post-hoc; no writes to proposals or packets from inspect routes.
3. **Read-only exposure does not create mutability** — GET-only inspect API; UI uses read-only controls.
4. **Deterministic legal handbook behavior remains intact** — delivery paths and citations are untouched; telemetry only reflects `delivery_mode` and related flags.
5. **Low-confidence memory/trace context remains secondary only** — prior counts are observational; they do not override retrieval.

## 7. WHAT THIS PASS IMPLEMENTED

- `app/services/telemetry/` — `build_turn_telemetry`, `telemetry_json_safe`, `TELEMETRY_SCHEMA_V1`.
- `app/services/scenario_memory/trace_read.py` — `list_recent_scenarios`, `serialize_readonly_trace_bundle`, `can_read_scenario`.
- `app/services/malone_service.py` — adds **`malone_telemetry`** to chat response (includes `cross_source_legal_policy_triggered` from existing `cross` flag).
- `app/api/malone_routes.py` — `GET /inspect/telemetry-schema`, `GET /inspect/traces`, `GET /inspect/traces/{id}`.
- `src/lib/maloneApi.js` — helpers for inspect endpoints.
- `src/components/malone/MaloneInspectionPanel.jsx` + `MalonePage.jsx` — optional read-only panel.
- `tests/test_readonly_copilot_telemetry.py` — telemetry shape, immutability, trace serialization, auth checks.
- `tools/debug_turn_telemetry.py` — sample telemetry printer.
- Tracking reports and `malone_readonly_copilot_json_telemetry_state.json`.

## 8. WHAT REMAINS DEFERRED

- **Pagination/cursors** for large trace histories (only `limit` on list).
- **Server-side redaction policies** per role beyond owner/admin vs self (e.g., field-level masking).
- **Centralized log shipping** to external analytics (explicitly out of scope; telemetry stays in API responses and DB reads).
- **E2E browser tests** for the inspection panel (manual verification only in this pass).

## 9. HARD-FAIL COMPLIANCE CHECK

| Requirement | Status |
|---------------|--------|
| No mutation controls for copilot or trace data via new surfaces | **Pass** — GET-only inspect API; UI read-only |
| Telemetry does not alter answer behavior | **Pass** — built after delivery; no feedback loop |
| Prior memory does not override current evidence | **Pass** — precedence unchanged; note is informational |
| Citation-first / deterministic legal behavior preserved | **Pass** — no changes to legal formatters or delivery logic |
| Single Malone path | **Pass** — same `handle_malone_request` |
| Tracking outputs produced | **Pass** — reports + state JSON under `tracking/reports/` |
