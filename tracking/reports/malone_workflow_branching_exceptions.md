# Branching and exceptions

## Branch extraction

- Regex captures sentences starting with **if / unless / when / in the event that**.
- Stored as `branch_conditions` with full sentence text (truncated).

## Relation to decision_reasoning

- Existing `exceptions` from normalized units remain authoritative for structured exception lists.
- Text-derived branches are **supplementary** and appear in `workflow_branch_hints`.

## Scope

No general-purpose condition evaluator; no branching engine. Malone still answers from evidence + guidance text only.
