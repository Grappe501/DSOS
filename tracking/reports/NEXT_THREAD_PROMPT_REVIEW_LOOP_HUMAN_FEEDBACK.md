# Next thread — review loop follow-on

## Done in this pass

- DB tables for review events + heads; Alembic `0008`.
- `/api/malone/review/*` API; `malone_governance` on Malone chat.
- Ranking and scenario-prior tweaks; minimal owner/admin review UI on Malone page.

## Suggested next steps

1. **Reviewer roles** — extend beyond owner/admin (e.g. `steward` role) with department-scoped artifact filters.
2. **Queue UX** — paginated `/queue` UI with filters by `artifact_type` and `current_review_state`.
3. **Notifications** — webhook or email on `risk_flag` / `needs_revision`.
4. **Deeper promotion gates** — optional blocking of `retrieval_ready` promotion until review head is `approved` (feature-flagged).
5. **Website pack manifest sync** — optional tool to mirror head state into a JSON sidecar for CI.

## Constraints

- Preserve single Malone path and evidence precedence.
- Do not add silent source rewrites.

## Active lane

Work only under `app/`, `src/`, `schemas/`, `alembic/`, `tracking/`, `tests/`, `tools/`.
