# Next thread prompt — business operating copilot (follow-on)

## Context

The first business operating copilot layer is implemented under `app/services/operating_copilot/`, wired in `malone_service.py`, enriched on the truth packet, and appended in smart-pattern and legacy formatters. Reports live in `tracking/reports/malone_*operating_copilot*`.

## Suggested next pass

1. **SOP depth**: Enrich `workflow_assembler` / SOP segment metadata so checkpoint and stop conditions surface more often in `action_steps` and copilot lines when runbooks are ingested.
2. **Product UX**: Optional read-only API fields or UI blocks that mirror `truth_packet["operating_copilot"]` without new agent paths (stay within allowed directories).
3. **Evaluation**: Curated scenario sets per source type mix with golden outputs for regression (pytest or JSON fixtures).
4. **Telemetry**: Log `primary_scenario`, `fallback_reason`, and `evidence_scope` in existing audit hooks where appropriate.

## Constraints to preserve

- One Malone path; no parallel copilot agent.
- Citation-first legal behavior; copilot remains appendix.
- Safe fallback when evidence is incomplete.

## Verification commands

```bash
python -m pytest tests -q
python -m compileall app tools tracking/scripts -q
npm run build
```
