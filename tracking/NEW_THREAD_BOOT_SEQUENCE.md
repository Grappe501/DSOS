# New Thread Boot Sequence

## Required first actions
1. Read `/tracking/current_state.json`
2. Read `/tracking/progress.json`
3. Read `/tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.7.0.md`
4. Read `/tracking/malone/MALONE_V1_MASTER_PLAN.md`
5. Read `/tracking/malone/malone_manifest_v1.json`
6. Run `/tools/project_map_audit.py`
7. Compare audit output with tracking
8. Only then begin implementation

## Required protection rules
- Do not move executable tooling into `/tracking`
- Do not move manifests/docs into `/tools`
- Do not change route namespace assumptions without updating both backend and frontend
- Do not let AI execution bypass deterministic validation

## Required output style
- Full-file replacements preferred
- Production-grade
- Minimal regressions
- Explicitly call out assumptions
