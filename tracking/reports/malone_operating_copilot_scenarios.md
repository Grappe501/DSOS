# Scenario routing (business operating copilot)

## Scenarios

| ID | Intent |
|----|--------|
| `next_steps` | What to do next, handling, first step |
| `role` | Pharmacist, technician, who owns, responsible |
| `exception` | What if, denied, blocker, exception |
| `escalation` | Escalate, compliance, stop workflow, notify |
| `operating_summary` | Short operational summary, top things, what matters |

## Mechanics

- **Question signals** increment per-scenario scores in `score_scenario_signals`.
- **Decision hints**: `operational_intent` of `escalation_focus` or `step_by_step` adds small boosts; presence of `escalations` / `exceptions` lists adds minor boosts.
- **Tie-break**: `_SCENARIO_TIE_ORDER` chooses the winner when multiple scenarios share the max score.
- **Default**: If the user message is operational but no scenario scores, primary defaults to `operating_summary` inside `build_operating_copilot_block` (from `none`).

## Inspectability

Every route returns `scores` and `reasons` for audit and debugging.
