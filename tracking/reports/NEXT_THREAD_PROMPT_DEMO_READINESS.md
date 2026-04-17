# Next Thread — Post-Demo Hardening

## Done

Demo env flags, presentation layer, `/demo/status`, UI badge/collapse/presets, `tools/demo_prompts.py`, tests, reports.

## Optional follow-ups

1. **Operator cheat sheet** — one-page PDF from `malone_demo_prompt_set.md` (out of repo if preferred).
2. **Stricter demo** — hide Malone Review panel behind admin-only route for owner demos (UI-only).
3. **Metrics** — log `demo.active` on audit events (privacy-sensitive; confirm policy first).

## Verify

`MALONE_DEMO_MODE=1 python -m pytest tests -q` and manual walkthrough of three flows.
