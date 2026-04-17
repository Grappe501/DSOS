# Cross-source strategy (legal + policy + SOP)

## Counts

`evidence_scope_summary` counts `items` per bundle when `enabled` is true. `cross_source` is true when more than one of legal, policy, or SOP has a positive count.

## Merge

`merge_units` concatenates normalized units from all lanes with stable lane labels. The copilot **does not** re-query the database; it uses bundles already built for the request.

## Strongest combinations

- **Legal + policy**: Both appear in `supporting_sources.source_types` when normalized units exist for each lane and bundles were loaded (e.g., cross-source intent or multi-target retrieval).
- **Policy + SOP**: Segment bundles both flow through `_units_from_segment_bundle` with appropriate `source_type` tagging.
- **Legal + policy + SOP**: Requires all three bundles populated for the turn; scope reflects item counts even when normalized merge is partial.

## Honesty

When only one source type has normalized units, uncertainty reasons include `single_source_type_only` even if raw items existed elsewhere without normalization.
