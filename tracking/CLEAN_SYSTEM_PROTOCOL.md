# DSOS Clean System Protocol

This file is the standing cleanup and handoff protocol for future DSOS threads.

## First priority on every takeover
Run these in order from project root:

1. `python tools/project_map_audit.py`
2. `python tools/self_verify_bootstrap.py`
3. `python tools/scaffold_size_audit.py`
4. `python scripts/build_map.py`
5. `python scripts/update_progress.py`

Do not begin feature work until the outputs are reviewed.

## What the new thread must determine
- which roots are active:
  - backend source of truth = `app/`
  - frontend source of truth = `src/`
- which roots are passive or historical:
  - `backend/app/`
  - `frontend/src/`
  - `dsos_replacements/`
- which artifacts are generated and should not be used as source of truth:
  - `.git/`
  - `.venv/`
  - `node_modules/`
  - `runtime_v5.db`
  - `test.db`

## Mandatory cleanup checks
- confirm tracking matches live code
- confirm workflow package health
- confirm approval and clarification services still resume workflows correctly
- confirm no new feature work is being added to passive roots
- confirm `scripts/update_progress.py` runs cleanly
- confirm size anomalies are explained before code changes

## Delivery standard
When changing production code:
- return only full-file replacements
- preserve path nesting exactly
- keep new workflow logic in `app/services/workflows/`
- do not reintroduce monolithic workflow logic into `app/services/workflow_service.py`

## Immediate priorities after cleanup
1. finish workflow package split
2. finish approval lifecycle completion
3. finish clarification state end-to-end
4. build internal DSOS retrieval layer
5. begin governed write execution
6. standardize migrations
