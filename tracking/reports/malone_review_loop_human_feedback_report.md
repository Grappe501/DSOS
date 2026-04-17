# Malone review loop + human feedback — pass report

## 1. WHY A REVIEW LOOP + HUMAN FEEDBACK LAYER IS NEEDED

Ingested knowledge, normalized units, operating copilot guidance, and scenario traces accumulate faster than informal review can track. A **structured, auditable** review layer lets trusted stewards approve, reject, flag risk, or request revision **without** pretending that governance replaces statutory text or retrieval-grounded citations. It closes the loop between system-generated artifacts and human accountability.

## 2. CURRENT GOVERNANCE LIMITATIONS

Before this pass, `NormalizedKnowledgeUnit.review_state` existed but there was **no unified feedback ledger** tying reviewer identity, outcomes, and history across artifact types. Scenario rows had `review_audit_status` with no standard workflow. There was **no narrow API** for recording human decisions at scale, and **no materialized “head”** row for review queues. Website pack entries and ingestion versions lacked a consistent review hook.

## 3. TARGET REVIEW LOOP ARCHITECTURE

- **Append-only events** (`malone_review_feedback_events`): every decision is stored with before/after state, outcome, notes, optional trust, and metadata.
- **Artifact heads** (`malone_review_artifact_heads`): latest state per `(artifact_type, artifact_id)` for queues and dashboards.
- **Domain sync (non-destructive)**: updates **governance columns** and `meta_json.human_review` blobs — never raw source bodies.
- **API** under `/api/malone/review` with **owner/admin** for writes and sensitive reads; artifact-type catalog for any authenticated user.
- **Malone integration**: `malone_governance` on chat responses summarizes review heads for normalized units referenced in the truth packet.

## 4. REVIEWABLE ARTIFACT MODEL

Generic references: `artifact_type` + `artifact_id` support:

| Type | ID | Domain effect |
|------|----|----------------|
| `normalized_unit` | `normalized_knowledge_units.id` | Updates `review_state`, optional `confidence_level` |
| `scenario_memory` | `malone_scenario_memories.id` | Updates `review_audit_status`, `meta_json.human_review` |
| `decision_trace` | `malone_decision_traces.id` | Merges `meta_json.human_review` |
| `operating_copilot_snapshot` | scenario memory id | Same as scenario + `operating_copilot_review` flag in meta |
| `website_pack_entry` | stable string (e.g. `allcare:page:…`) | Events + head only |
| `ingestion_source_version` | `ingestion_source_versions.id` | Merges `meta_json.human_review`, `promotion_ready` hint |

Outcomes: `approved`, `rejected`, `needs_revision`, `informational`, `risk_flag`.

## 5. TRUST / PROMOTION / FEEDBACK INTERACTION

- **Normalized retrieval**: `review_rank` prefers higher review tiers (`approved` > `reviewed` > `system_generated` > `under_review` > draft/needs_revision; rejected/superseded lowest).
- **Scenario priors**: a **small** similarity boost applies when `review_audit_status` is `approved` and source-version conflict suppression does not apply — still secondary to current evidence.
- **Promotion**: `GET /api/malone/review/promotion/ingestion-source-version/{id}` combines DB `retrieval_ready` with review-head approval as an **advisory** signal (validation gates remain authoritative).

## 6. SAFETY / PRECEDENCE MODEL

1. **Current source-grounded evidence outranks** human memory, feedback, and review labels.
2. **Review state influences trust and surfacing**, not the underlying legal excerpt or ingestion segment text.
3. **Review records are append-only**; rejections do not delete history.
4. **Rejected normalized units stay blocked** from augmentation per existing `unit_is_blocked` rules.
5. **Deterministic legal formatting** is unchanged; tests assert formatter output stability independent of governance metadata.

## 7. WHAT THIS PASS IMPLEMENTED

- ORM + Alembic `0008` + `schemas/malone_review_feedback_v0.sql` reference.
- Package `app/services/review_feedback/` (store, queries, registry, promotion/trust helpers, governance hints, safety guard on forbidden meta keys).
- Router `app/api/review_feedback_routes.py`; registered in `app/main.py`.
- `malone_service` adds **`malone_governance`**.
- `review_state` vocabulary extended (`under_review`, `needs_revision`); ranking/caveat paths updated.
- Scenario prior list includes `review_audit_status_then`.
- UI: `MaloneReviewPanel.jsx` (owner/admin only) + `maloneApi.me` / `reviewSubmitFeedback`.
- Tests: `tests/test_review_loop.py`.

## 8. WHAT REMAINS DEFERRED

- Department-scoped reviewers and fine-grained RBAC beyond owner/admin.
- Full review queue UI with filters, assignment, and SLA metrics.
- Automatic notifications on `risk_flag`.
- Deep integration of review heads into every ingestion validation gate (currently advisory).

## 9. HARD-FAIL COMPLIANCE CHECK

| Rule | Status |
|------|--------|
| No feedback overriding current source-grounded evidence | **Pass** — precedence documented; retrieval uses review as tie-break / trust only |
| Citation-first legal behavior preserved | **Pass** — no formatter changes; deterministic test |
| No uncontrolled editing platform | **Pass** — narrow API; no bulk source editor |
| Single Malone path | **Pass** — governance is additive metadata |
| Tracking outputs present | **Pass** — this report + state JSON + architecture notes |
