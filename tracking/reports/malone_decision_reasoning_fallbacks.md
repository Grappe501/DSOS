# Decision reasoning — fallbacks and safety

## Layer disabled

| Condition | Behavior |
|-----------|----------|
| `MALONE_DECISION_REASONING_ENABLED` resolves false | No `decision_workflow` augmentation beyond disabled stub; default follows normalized retrieval gate |
| User sets explicit off | Same as above |

## Empty or unusable decision context

| Condition | Behavior |
|-----------|----------|
| No normalized units merged from any bundle | `fallback_reason: no_normalized_units_for_decision_layer`; operational section **omitted** |
| `should_emit_structured_sections` false | Formatter skips operational appendix |

## Trust and review

- `trust_tier` aggregated from unit review/confidence ranks.
- `caution_low_trust_dominant` when all merged units are draft/unknown-confidence.
- Draft/unknown units still allowed in grouping but flagged in the answer appendix.

## Downgrade chain

1. Prefer **structured decision appendix** when enabled and no `fallback_reason`.
2. Else user sees **normalized blocks only** (per-chunk/segment, existing behavior).
3. Else **raw excerpts only** if normalization absent entirely.

## Legal path

- Citation-first ordering unchanged; decision section is **never** inserted before excerpts.
- Supplementary forbidden-claim lines added when structured section emits.
