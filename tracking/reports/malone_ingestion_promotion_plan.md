# Promotion and activation plan

## Goals

Separate **“stored in DB”** from **“eligible for operational retrieval and downstream governance”** without entangling Malone’s chat orchestration.

## States

**Source (`ingestion_sources.lifecycle_status`):** `registered` → `active` (when a version is promoted to active) → `archived` / `superseded` (future administrative transitions).

**Version (`ingestion_source_versions.status`):** `draft` → `validated` (legal path after successful ingest) → `promoted_active` — or direct promotion from draft for generic profiles when validation passes. `archived` / `superseded` for retirement.

**Flags:** `retrieval_ready` on versions and segments set true when promotion applies (can be refined per profile later).

## Records

`ingestion_promotions` captures `from_status`, `to_status`, `promotion_outcome` (`pending` | `applied` | `reverted`), optional `actor` and `reason`.

## Automation

`run_business_ingest(..., promotion_mode=...)`:

- `none` — no promotion.
- `if_pass` — promote only when validation is **PASS**.
- `if_pass_or_warn` — promote on **PASS** or **PASS_WITH_WARNINGS**.

Implementation: `promotion.promote_source_version`.

## Manual / API follow-up

Future admin endpoints can call the same helpers with explicit actor and reason strings; not implemented in this pass.

## Compliance note

Promotion is **ingestion governance**. It does not change Malone proposal logic or legal evidence flags.
