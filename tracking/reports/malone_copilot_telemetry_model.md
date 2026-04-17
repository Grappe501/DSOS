# Copilot telemetry model (`malone_telemetry`)

## Purpose

Provide a **stable, versioned** view of routing and scope decisions for a single Malone turn. This is **observational metadata** only: it must not be used to drive retrieval, citations, or rendering.

## Schema

- **`schema_version`**: integer (currently `1`).  
- **`read_only`**: always `true` for API consumers.  
- **`precedence_note`**: echoes `PRECEDENCE_NOTE` from scenario memory precedence (informational).  
- **`intent`**: `target`, `mode`.  
- **`proposal_id`**: current proposal id string.  
- **`scenario_route`**: operating copilot primary scenario + `router_payload` (`scenario_route` from the copilot block) + trimmed `route_reasons`.  
- **`operating_copilot`**: `enabled`, `primary_scenario`, `fallback_reason`, `emit_minimal_only`, `evidence_scope`, `source_types_present`.  
- **`decision_workflow`**: `enabled`, `fallback_reason`, `sources_present`, `partial_workflow`.  
- **`answer_pattern`**: pattern id + `packet_meta` answer pattern labels.  
- **`fallbacks`**: copilot/workflow/verification reason lists.  
- **`evidence_scope`**: source types with items, item counts, cross_source from copilot scope.  
- **`cross_source`**: evidence-scope cross-source plus **`cross_source_legal_policy_triggered`** (from the existing `cross` flag in `malone_service`).  
- **`delivery`**: `delivery_mode`, `deterministic_legal_mode` bucket, `verified`.  
- **`scenario_memory`**: prior analog count, `emit_in_answer`, packet_meta prior count.  
- **`trace_ids`**: `scenario_memory_id`, `decision_trace_id` when persisted.  
- **`inspect_routes`**: relative paths to list/detail trace APIs.

## Construction

Implemented in `app/services/telemetry/malone_turn_telemetry.py` as **`build_turn_telemetry(...)`** — pure function, no database access.
