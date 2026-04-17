# Malone Company Knowledge Review + Promotion — Pass Report

## 1. WHY A COMPANY KNOWLEDGE REVIEW + PROMOTION LAYER IS NEEDED

Internal company artifacts (policies, SOPs, training, website-derived pack lines) flow through the same ingestion and normalization path as operational evidence, but they carry operational and reputational risk if treated as “trusted” before a steward has reviewed them. A dedicated review and promotion layer lets humans attach decisions and move artifacts along an explicit lifecycle (draft → reviewed → approved → active) without inventing a second CMS or rewriting source text. Malone remains one system: governance metadata and promotion records sit beside ingestion control and review events.

## 2. CURRENT COMPANY-KNOWLEDGE GOVERNANCE LIMITATIONS

Before this pass, human review outcomes were partially modeled (normalized units, scenarios, traces, ingestion versions) but lifecycle vocabulary for “company knowledge” was not unified, outcomes like `ready_for_promotion` and `hold_for_review` were missing, and there was no narrow API to list internal company source versions with promotion hints or to activate a version only after explicit approval. Website pack entries could only be reviewed via generic artifact heads without a dedicated queue helper. Telemetry could surface normalized unit heads but not ingestion-version promotion signals next to policy/SOP evidence.

## 3. TARGET REVIEW + PROMOTION ARCHITECTURE

- **Single path**: `submit_review_feedback` → append-only `malone_review_feedback_events` + `malone_review_artifact_heads`; domain sync updates governed columns and `meta_json.human_review` on `IngestionSourceVersion` without editing segment body text.
- **Promotion**: `promote_source_version` / `archive_source_version` in `app/services/ingestion_control/promotion.py` remain the only mechanical activation/archive levers; `company_knowledge_promotion.py` orchestrates guarded promotion after head state `approved`.
- **API**: Owner/admin routes under `/api/malone/review/company-knowledge/*` for candidates, website-pack heads, promote-version, and archive-version.
- **Read-only surfacing**: `build_governance_hints_for_turn` includes `ingestion_source_versions` with review heads and promotion signals when policy/SOP bundles expose `ingestion_source_version_id`.

## 4. ARTIFACT STATE MODEL

- **Lifecycle labels** (metadata, `company_knowledge_lifecycle` in human_review patch for ingestion versions): discovered, ingested, validated, under_review, reviewed, approved_for_use, active, rejected, superseded, archived (see `company_knowledge_states.py` and mapping via `lifecycle_from_review_outcome`).
- **Artifact heads** use string states per artifact type (e.g. ingestion version head: `approved`, `validated`, `under_review`, `rejected`, aligned with review outcomes).
- **Mechanical version status** remains on `IngestionSourceVersion.status` (`promoted_active`, `archived`, etc.) and is driven only by promotion/archive services, not by LLM edits.

## 5. TRUST / READINESS / FEEDBACK INTERACTION

- Review outcomes update normalized unit `review_state` and confidence where applicable; `review_rank` in normalized retrieval continues to prefer higher-review states when augmenting answers (tie-breakers only).
- `ingestion_source_version_promotion_signal` exposes `promotion_hint`, `review_head_approved`, and staging for `validated` heads (`ready_for_promotion` outcome).
- Governance hints in Malone responses are explicitly non-authoritative and listed alongside a precedence note.

## 6. SAFETY / PRECEDENCE MODEL

- Source-grounded citations and legal deterministic paths are unchanged; promotion does not rewrite `body_text` or chunk text.
- `assert_no_source_text_mutation_fields` still blocks silent overrides of `source_text`, `body_text`, etc.
- Rejected and superseded artifacts retain append-only event history.
- No blanket auto-promotion: activation requires an approved review head (default) before `promote_ingestion_version_to_active_trusted`.

## 7. WHAT THIS PASS IMPLEMENTED

- Extended review outcomes: `ready_for_promotion`, `hold_for_review`.
- Lifecycle mapping for ingestion source versions and richer `promotion_ready` (true for approved and ready_for_promotion).
- `company_knowledge_promotion.py`: list internal company source versions with heads/signals, website pack head listing, guarded promote, archive with supersede metadata.
- API routes for company-knowledge queue and actions.
- `governance_hints`: ingestion version promotion signals next to policy/SOP evidence.
- `promotion_signals`: staging awareness for validated heads.
- Client helpers in `src/lib/maloneApi.js`.
- Tests in `tests/test_company_knowledge_review_promotion.py`.
- Tracking reports (this file and companions under `tracking/reports/`).

## 8. WHAT REMAINS DEFERRED

- Rich UI for stewards (beyond API + existing Malone review feedback); optional compact panel can be added later.
- Automatic linkage from every workflow-derived artifact to a single review queue row (currently covered via existing artifact types where registered).
- Deeper integration of website pack lines with filesystem manifest diffs (heads remain DB-backed; manifest stays external).
- Explicit FK from normalized units to promotion records (optional; events + heads suffice for audit today).

## 9. HARD-FAIL COMPLIANCE CHECK

| Requirement | Status |
|-------------|--------|
| No edits under `backend/`, `frontend/`, `dsos_replacements/` | Pass (changes in `app/`, `src/`, `tests/`, `tracking/` only). |
| Review/promotion does not override source-grounded evidence | Pass (metadata and readiness only). |
| Citation-first legal behavior preserved | Pass (no legal path changes; governance hints additive). |
| No auto-promote-all | Pass (explicit promote endpoint + default prior approval). |
| No uncontrolled editing system | Pass (append-only events, narrow admin routes). |
| Tracking outputs produced | Pass (reports + state JSON in `tracking/reports/`). |
