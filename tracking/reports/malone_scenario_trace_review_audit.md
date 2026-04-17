# Review / audit note — scenario memory & decision traces

## Inspectability

- Rows are plain JSON in SQLite/Postgres-compatible columns; `tools/debug_scenario_memory.py` lists recent scenarios or prints trace keys.
- `proposal_id` links each scenario memory to `malone_proposals` for correlation with user actions.

## Review fields

- **`memory_status`**: `active` (default), extensible to `archived` / `rejected` for governance workflows.
- **`review_audit_status`**: `pending` default; product may later mark `cleared` / `flagged` without changing Malone’s primary path.

## Audit service

This pass does not replace `audit_service` / `log_malone_action`; it adds **durable relational** artifacts for long-horizon comparison. Operational audits can join proposal → scenario → trace.
