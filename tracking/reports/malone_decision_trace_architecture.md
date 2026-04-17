# Decision trace architecture

## Contents

Each trace stores:

| Field | Role |
|-------|------|
| `answer_pattern_json` | Smart-pattern selection / rendered pattern |
| `decision_workflow_json` | Full serialized `decision_workflow` block |
| `source_evidence_map_json` | Unit → anchor map from decision layer |
| `normalized_unit_refs_json` | Stable unit ids for audit |
| `fallback_flags_json` | Decision + copilot + pattern fallbacks |
| `packet_meta_snapshot_json` | Key `packet_meta` at delivery time |
| `operating_copilot_snapshot_json` | Optional copilot block |
| `verification_snapshot_json` | Delivery verification dict |
| `deterministic_legal_mode` | Legal vs other deterministic delivery |

## Serialization

`dumps_limited` truncates oversized JSON with a `_truncated` marker so storage stays bounded while remaining honest about loss.
