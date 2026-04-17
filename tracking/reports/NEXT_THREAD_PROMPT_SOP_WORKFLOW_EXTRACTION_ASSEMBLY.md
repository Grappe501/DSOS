# Next thread — SOP / workflow extraction & assembly

## Completed

- `workflow_extraction` + `workflow_assembly` integrated into `build_action_plan`.
- Copilot step lines show optional stop/checkpoint hints; guardrails for weak extraction.

## Recommended next steps

1. **Ingestion:** Improve normalized `structured_facets_json` for SOP segments (step_order, role) at ingest time so extraction complements DB fields rather than carrying all signal.
2. **UI:** Surface `workflow_checkpoint_view` in internal review tools (allowed lanes only).
3. **Evaluation:** Golden SOP fixtures with expected `numbered_steps` and role keys for regression.

## Verify

```bash
python -m pytest tests -q
python -m compileall app tools -q
npm run build
python tools/debug_workflow_extraction.py --sample
```
