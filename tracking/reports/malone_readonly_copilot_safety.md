# Read-only copilot / telemetry safety

## Precedence

- **Current evidence wins.** `PRECEDENCE_NOTE` is included in `malone_telemetry` as a reminder; it does not change retrieval or answers.  
- **Prior analogs** appear only in `scenario_memory` counts and optional `scenario_memory_context` in the truth packet; they remain **secondary** and gated by existing guardrails.

## No behavioral coupling

- Telemetry is computed **after** `verification` and proposal update; it is not an input to `render_conversational_response` or deterministic formatters.  
- Inspect APIs are **GET-only** and do not commit transactional side effects beyond normal read queries.

## UI

- Inspection UI is **read-only** (textareas with `readOnly`, no forms that POST trace or copilot edits).  
- Hidden by default to avoid cluttering the primary Malone experience.

## Deterministic legal

- Legal/policy/SOP deterministic delivery code paths are **unchanged** by this pass. Telemetry reflects `delivery_mode` for audit only.
