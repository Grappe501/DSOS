# Checkpoints and stop conditions

## Extraction

- **Checkpoints:** Sentences anchored on verify / confirm / checkpoint / ensure / validate / document that / sign off.
- **Stops:** Phrases like “do not proceed,” “stop if,” “halt,” “must not continue,” “discontinue if.”

## Assembly

- Stored per step under `workflow_extraction.checkpoints` and `.stop_conditions`.
- Aggregated in `workflow_checkpoint_view` for audit and optional UI.
- Operating copilot may append a **short** bracketed hint on the first matching stop or checkpoint per step line.

## Safety

Signals are **heuristic**; when `workflow_extraction_assessment.use_minimal_workflow_guidance` is true, users see extra forbidden-claim strings on the truth packet.
