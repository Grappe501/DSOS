# SOP / workflow fallbacks

## Sparse extraction

When `partial_workflow` is true and no step has `extraction_confidence == high`, `use_minimal_workflow_guidance` is set. Users get:

- Extra **forbidden_claims** (regex-derived checkpoints not exhaustive).
- Operating copilot continues to use uncertainty and existing minimal modes when evidence is thin.

## Ordering

If numbered steps are missing, bullet lists may still contribute medium confidence; pure narrative may yield **low** confidence only.

## Upstream fallbacks (unchanged)

Smart patterns, normalized retrieval, raw evidence, and legal citation-first behavior remain the ultimate backstops.
