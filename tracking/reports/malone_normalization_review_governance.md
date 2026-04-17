# Normalization review and governance

## Review states

| State | Meaning |
|-------|---------|
| `draft` | Placeholder or manual stub (not used by default in v1) |
| `system_generated` | Default for all units produced by this pass |
| `reviewed` | Human reviewed content/metadata |
| `approved` | Cleared for downstream use (e.g. Malone prompts, promotion) |
| `rejected` | Do not use; keep for audit |
| `superseded` | Replaced by a newer unit (`superseded_by_unit_id`) |

## Events

`normalized_knowledge_review_events` records `from_state` → `to_state`, optional `actor`, `reason`.

## Who reviews what

- **Legal units**: Subject-matter / compliance review before `approved`; statutory text unchanged—review focuses on **normalization labels** (type, requirement level, summary).
- **Policy units**: Policy owner / internal compliance; often same steward as `ingestion_sources.owner_steward`.

## Tie-in to promotion

- Ingestion **promotion** (`ingestion_promotions`) gates raw material; normalization **approval** gates structured knowledge used in agent workflows. A future pass may require `approved` normalized units only when `ingestion_source_versions.status` is `promoted_active`.

## What this pass did not automate

- No auto-transition to `reviewed`/`approved`.
- No email / workflow engine—only schema + audit table.
