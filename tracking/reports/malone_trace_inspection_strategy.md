# Trace inspection strategy

## Data model

- **`malone_scenario_memories`**: one row per persisted scenario (linked to `malone_proposals`).  
- **`malone_decision_traces`**: one row per scenario (1:1), holding JSON snapshots of answer pattern, decision workflow, evidence maps, fallbacks, packet_meta, operating copilot snapshot, verification snapshot.

## Read path

1. **List** — `list_recent_scenarios` orders by `created_at` descending, filters by `actor_user_id` unless the role is `owner` or `admin`.  
2. **Detail** — `serialize_readonly_trace_bundle` loads the linked `MaloneDecisionTrace`, parses JSON text columns with `loads_safe`, and applies `_maybe_truncate_json_obj` for very large objects in HTTP responses.

## Client usage

- Prefer **`scenario_memory_id`** from `malone_telemetry.trace_ids` or `truth_packet` after a chat turn.  
- Call **`GET /api/malone/inspect/traces/{scenario_memory_id}`** for the full read model.  
- The optional **`MaloneInspectionPanel`** button triggers the same GET via `maloneApi.getInspectTrace`.

## Security

Inspect endpoints require authentication (`get_current_user`). Row-level access uses the same actor-vs-admin pattern as `/api/malone/proposals`.
