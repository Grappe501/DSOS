# Escalation and uncertainty

## Escalation content

Escalation strings come from grouped normalized units in the decision/workflow plan (`build_escalation_lines`). Scenario routing can prioritize `escalation` when the user asks about compliance handoffs or stopping a workflow.

## Uncertainty levels

`assess_uncertainty` sets `level` to `high` when:

- No normalized units merged, or
- Partial workflow flagged, or
- Low-trust / draft-heavy unit mix.

Single-source-type evidence adds a reason (breadth limitation).

## User-visible uncertainty

`uncertainty_note_text` is included in guidance and, in minimal fallback, may be the primary user-visible note alongside “rely on citations and excerpts above.”

## No hidden risk

The distinction block always separates **required**, **recommended**, **uncertain**, and **escalate** when full guidance is emitted.
