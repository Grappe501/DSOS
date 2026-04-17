# Read-only copilot / trace exposure architecture

## Layers

1. **Chat response (primary UX)**  
   `POST /api/malone/chat` returns the existing envelope plus **`malone_telemetry`**: a flattened, versioned summary for dashboards and debugging. The full **`truth_packet`** still contains authoritative `operating_copilot`, `decision_workflow`, and evidence bundles.

2. **Inspect API (narrow, authenticated)**  
   - `GET /api/malone/inspect/telemetry-schema` — documents `malone_telemetry` fields.  
   - `GET /api/malone/inspect/traces` — recent scenario memory rows for the caller.  
   - `GET /api/malone/inspect/traces/{scenario_memory_id}` — parsed snapshots from `malone_scenario_memories` + `malone_decision_traces`.

3. **Optional UI**  
   `MaloneInspectionPanel` is hidden by default, toggled via a button, with state in `localStorage` (`malone_inspect_open`). It only displays JSON in **read-only** `<textarea>` elements and optionally loads trace detail through the GET API.

## Non-goals

- No separate observability service or trace-editing UI.  
- No write paths under `/inspect/`.  
- No second copilot or memory-first answer pipeline.
