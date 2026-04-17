# Next Thread — Department Intake + Operations Mapping (follow-on)

## Done in this pass

Models, migration, intake + map services, deterministic follow-ups, APIs, minimal UI, tests, tracking reports.

## Recommended next steps

1. **Voice handoff** — From `VoiceInputButton` / listen callback, POST transcript to `operationsMapPostAnswer` with `entry_mode: voice_transcript` when user is in “intake mode” (UI toggle).
2. **Smarter parsing** — Optional structured templates per `question_key` (tables, bullet extraction) still without LLM.
3. **Governance** — Register materialized map entities as review artifacts (`operations_department` head type) if product wants formal approval.
4. **Validation gates** — Require minimum follow-up resolution before `materialize` (config).

## Verify

- `alembic upgrade head` (deploy)
- `python -m pytest tests -q`
- `npm run build`
