# Next Thread — Company Knowledge Review + Promotion (follow-on)

## Context

The Company Knowledge Review + Promotion pass added outcomes (`ready_for_promotion`, `hold_for_review`), `company_knowledge_promotion` services, `/api/malone/review/company-knowledge/*` routes, governance hint enrichment for ingestion versions, and tests + tracking reports.

## Suggested next work

1. **Steward UI** — Minimal panel on `MalonePage` (owner/admin): table of `candidates`, actions to submit feedback, promote, archive; link to existing `/review/feedback` patterns.
2. **Validation gates** — Optionally require `overall_validation_status == PASS` on linked ingest jobs before `promote-version` (config flag).
3. **Website pack** — Optional tool to seed `website_pack_entry` heads from `build_allcare_website_ingestion_pack.py` output for bulk review queues.
4. **Metrics** — Counters: counts by head state per `source_type` for operational dashboards (read-only).

## Constraints

- Keep a single Malone governance path; do not add a second content platform.
- Do not allow promotion metadata to override citations or legal deterministic delivery.

## Verification

- `python -m pytest tests -q`
- `python -m compileall app tools -q`
- `npm run build`
