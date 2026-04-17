# Fallbacks and safety (operating copilot)

## Disable gates

| Condition | Result |
|-----------|--------|
| `MALONE_OPERATING_COPILOT_ENABLED` off (or decision reasoning off when env unset) | Block `enabled: false` |
| No evidence items across bundles | `no_evidence_items_for_copilot` |
| Message not operational | `not_operational_query` |

## Thin evidence

When items exist but merged normalized units are empty and uncertainty is high, and there is no structured decision content, the copilot may set `emit_minimal_only` with an uncertainty note instead of a full plan.

## Emission rules (`should_emit_operating_copilot_section`)

- Enabled + minimal fallback → emit short safe section.
- Enabled + other `fallback_reason` → **do not** emit (avoids half-fabricated operational prose).

## Downstream answers

If the copilot does not emit, users still receive smart patterns, normalized retrieval, or standard citation-first bodies—the copilot never replaces those layers.
