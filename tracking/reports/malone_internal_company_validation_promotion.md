# Validation and promotion (internal batch)

## Per source

Existing ingestion validation applies (`PASS` / `PASS_WITH_WARNINGS` / `FAIL` from control plane).

## Batch

`batch_validation_status` aggregates:

- **Failures** — ingest did not complete or validation `FAIL`.
- **Warnings** — empty tree, skipped inactive files, normalization exceptions, per-file `PASS_WITH_WARNINGS`.

Uses `decide_overall_status` for the batch rollup.

## Promotion

CLI defaults to **`none`**. Operators may use `if_pass` or `if_pass_or_warn` when business rules allow—**never** implied by this pass.

## Conservative stance

Internal company content should be **reviewed** before broad `retrieval_ready` promotion; manifests flag `ready_for_review` for policy/SOP/compliance paths.
