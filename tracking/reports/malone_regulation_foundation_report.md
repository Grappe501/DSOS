# Malone Regulation Knowledge Foundation — Pass Report

**Pass date:** 2026-04-16  
**Scope:** Deterministic scaffolding and data design only (no full Q&A, no upload UI).  
**Active lanes honored:** `app/`, `src/`, `tracking/` (plus `schemas/`, `alembic/` for artifacts explicitly requested).

---

## HARD FAIL CONDITIONS

A regulation / knowledge foundation pass is **incorrect** if it:

| # | Condition |
|---|-----------|
| 1 | Modifies **`backend/`**, **`frontend/`**, or **`dsos_replacements/`** (passive lanes for this workstream). |
| 2 | **Replaces existing Malone behavior wholesale** instead of additive hooks (intent branch, truth-packet evidence, etc.). |
| 3 | **Creates scaffolds with no declared integration purpose** — each module must document Purpose, Role in Malone, inputs/outputs (see scaffold docstrings). |
| 4 | **Proposes a schema without versioning and citations** — at minimum immutable **source versions** plus **citation** rows/keys anchored to chunks (`schemas/regulation_knowledge_v0.sql`). |
| 5 | **Skips tracking outputs** — human report, machine-readable state, module/schema/API plans, next-thread prompt as required by the pass. |
| 6 | **Builds speculative Q&A behavior without the source registry foundation** — grounded answers require persisted **sources → versions → chunks → citations** before chat behavior is expanded. |

**This pass:** None of the above are violated (passive roots untouched; Malone behavior unchanged; scaffolds document Malone integration; schema includes `regulation_source_versions` + `regulation_citations`; tracking artifacts present; no production Q&A added).

---

## 1. CURRENT ACTIVE-LANE MALONE REALITY

### What Malone currently does

- **HTTP surface:** `POST /api/malone/chat` accepts `{ "message": string }` and returns a rich payload (intent, proposal record, workflow state, truth packet, rendered output, verification). Supporting endpoints: `GET /api/malone/proposals`, `GET /api/malone/capabilities`, `GET /api/malone/agents` (admin stub). See `app/api/malone_routes.py`.
- **Core loop:** `handle_malone_request` in `app/services/malone_service.py` classifies intent, creates a **MaloneProposal** row, validates the proposal envelope, starts a **workflow instance** for governed execution, builds a **truth packet** (`truth_packet_service`), optionally **renders** via OpenAI (`openai_service`) with **render verification** (`render_verifier`), and persists delivery metadata on the proposal path used by the UI.
- **Safety model:** No LLM text is delivered without passing the existing verification path tied to the truth packet; web search is gated by env and truth-packet retrieval rules. This matches doctrine in `tracking/malone/MALONE_V1_MASTER_PLAN.md` and `tracking/NEXT_PHASE_MASTER_BUILD_PLAN_v0.8.0.md`.

### What code paths already exist

| Area | Location | Role |
|------|----------|------|
| Routes | `app/api/malone_routes.py` | Chat, proposals, capabilities |
| Orchestration | `app/services/malone_service.py` | Intent → proposal → workflow → truth → render |
| Truth assembly | `app/services/truth_packet_service.py` | Deterministic facts for rendering |
| LLM render | `app/services/openai_service.py` | Structured render + optional web |
| Proposals | `app/services/proposal_service.py` | Persistence and serialization |
| Workflows | `app/services/workflow_service.py` + `app/services/workflows/` | Execution spine, approvals/clarifications |
| Clarifications | `app/services/clarification_service.py` | Resume hooks for blocked workflows |
| Frontend | `src/pages/MalonePage.jsx`, `src/components/malone/*`, `src/lib/maloneApi.js` | Output-first UI; sources list for web results |

### What can be reused directly

- **Truth packet + verification pipeline:** New regulation answers should feed *additional* structured evidence (chunk IDs, citation keys, version IDs) into the truth packet builder in a later pass—not replace it.
- **Proposal + audit trail:** `MaloneProposal` IDs are the natural foreign key for **answer traces** (`regulation_answer_traces.proposal_id` in the SQL proposal).
- **Workflow engine:** Ingestion jobs can stay outside Malone workflows initially; long-running ingest can use the same audit/logging style as existing services.
- **Frontend pattern:** `maloneApi.chat` remains the single user entry until a dedicated regulation mode is added; no change required for this pass.

**Assumption:** SQLAlchemy models for regulation tables are not wired in this pass; `Base.metadata.create_all` in `app/main.py` will not create the new tables until models exist or migrations are applied. The Alembic draft `0002` is the supported path to persist schema.

---

## 1a. EXPLICIT FOUNDATION QUESTIONS

### 1. Which existing Malone services should remain unchanged in this pass?

Treat these as **do not refactor or re-scope** for regulation work until a later bounded slice:

- **`app/services/malone_service.py`** — Keep `handle_malone_request`’s overall sequence (intent → proposal → workflow → truth packet → render → verification → persistence). Regulation support should arrive as **additive** branches or helpers, not a rewrite.
- **`app/services/openai_service.py`** — Render contract and structured output shape stay stable; regulation evidence should feed **inputs** to render, not fork a second LLM path.
- **`app/services/render_verifier.py`** — Verification rules remain the gate; regulation work extends **what** is verified (citations, evidence IDs), not remove verification.
- **`app/services/proposal_service.py`** — Proposal create/update/serialize behavior and envelope semantics stay as-is; regulation traces **reference** proposals via FK.
- **`app/services/workflow_service.py`** and **`app/services/workflows/`** — Existing schedule/governed execution flows must not be broken; regulation ingestion jobs do not need to own the workflow engine on day one.
- **`app/api/malone_routes.py`** — No new routes required for this foundation pass; future regulation endpoints (if any) are additive.
- **`app/services/intent_service.py`** — Existing intent classification for schedules and current modes stays; any regulation intent is a **narrow extension** later.

Services that may receive **small, optional extensions** in a *future* pass (not required to stay byte-identical forever, but should not be destabilized now): **`truth_packet_service.py`** (optional `regulation_evidence` block), **`intent_service.py`** (regulation routing).

### 2. Which existing Malone services are the most natural integration points for regulation ingestion?

| Integration point | Why |
|-------------------|-----|
| **`truth_packet_service.py`** | Single place to attach **deterministic regulation evidence** (chunk IDs, citation keys, version IDs) before render—aligned with “truth packet first” doctrine. |
| **`malone_service.py`** | After intent resolution, a future branch can call retrieval/compliance and pass results into the truth packet builder—**one** orchestration spine. |
| **`intent_service.py`** | Routes user messages toward regulation Q&A vs existing modes without new HTTP surfaces initially. |
| **`proposal_service.py` / `MaloneProposal`** | Natural anchor for **`regulation_answer_traces.proposal_id`** and delivery audit. |
| **`app/services/audit_service.py` / `log_malone_action` patterns** | Same audit style for ingestion milestones and trace logging. |
| **`render_verifier.py`** | Citation/evidence checks can extend verification payloads alongside existing claim checks. |

Ingestion **writing** to SQL should live in **`app/services/ingestion/`** + **`knowledge/`** with DB access; it should **not** bypass proposal/truth/verify for user-visible answers.

### 3. What is the smallest safe SQL foundation that unlocks future regulation Q&A?

The **minimum** schema that is both **auditable** and **retrieval-ready** (lexical first) is:

1. **`regulation_sources`** — Logical identity (stable key, jurisdiction, authority).
2. **`regulation_source_versions`** — Immutable version row (effective/superseded, status, checksum/storage pointer).
3. **`regulation_chunks`** — Text + ordinal + `retrieval_ready` + optional `embedding_ref` placeholder.
4. **`regulation_citations`** — Stable `citation_key` + `anchor_json` linking UI/audit to chunks.

Everything else in v0 (`regulation_tags`, `regulation_chunk_tags`, `regulation_ingestion_jobs`, `regulation_answer_traces`) is **highly recommended** for operator workflow and compliance audit, but the **smallest unlock** for “grounded Q&A later” is **sources + versions + chunks + citations**. The delivered **`0002`** migration includes the full v0 set so jobs and traces do not require a second migration scramble.

### 4. What pieces must be built before embeddings/vector search are added?

1. **Persisted chunks** with stable primary keys and **deterministic ordinals** within a version.
2. **Citation rows** (or equivalent keys) so every retrieved segment has a **stable citation anchor**—vectors without citations are unsafe for pharmacy compliance.
3. **Ingestion path** that can populate chunks from at least one real document shape (even a single PDF or text fixture).
4. **Lexical retrieval MVP** (FTS, `LIKE`, or external index) to validate **end-to-end** query → chunk → citation before investing in embedding infrastructure.
5. **Version/effective-date semantics** (even rule-of-thumb) so retrieval does not mix superseded and current text blindly.
6. **Storage decision for vectors** (blob in SQLite vs sidecar file vs Postgres/pgvector later)—embeddings are **not** the first storage problem; **identity and provenance** are.

### 5. What can be done now without increasing duplicate-lane confusion?

- **Work only in active lanes:** `app/` (services under `app/services/ingestion|knowledge|retrieval|compliance|assistant`), `schemas/`, `alembic/`, `tracking/`.
- **Do not** add parallel regulation stacks under **`backend/`**, **`frontend/`**, or **`dsos_replacements/`**.
- **Do not** copy Malone chat logic into new folders; keep **one** Malone entry (`malone_service`) and **library modules** that are imported when needed.
- **Tracking artifacts** (`tracking/reports/*.md`, `*.json`) document intent for the next thread—reduces the chance someone “re-discovers” regulation in a passive root.
- **Import-only scaffolds** (no new routes, no `main.py` wiring) avoid behavioral drift while the team agrees on ORM + first ingest.

### 6. What is the cleanest next pass after this one?

**One vertical slice:** *migration applied + SQLAlchemy models + one ingestion job that persists real chunks + lexical search returns those chunks + optional feature-flagged `regulation_evidence` stub in `truth_packet_service` (empty when no hits).*

That pass proves **data** and **retrieval** without committing to embeddings, without a new UI, and without forking Malone. The pass after *that* wires intent routing, citation display in the existing Malone output panel, and `regulation_answer_traces` on successful delivery.

---

## 2. REGULATION ENGINE TARGET

### What the regulation assistant must do

- Answer **pharmacy regulation** questions using **only** (or primarily) **ingested handbook content** with **explicit citations** (section, version, jurisdiction, effective dates).
- Support **updates over time**: new handbook versions, supersession, and “what was true as of date X” when explicitly scoped.

### Why a source-grounded approach is required

- Regulatory answers are **liability-sensitive**. The existing system already enforces “truth packet first” and verification before delivery; regulation content must be **evidence-backed** in the same spirit, with **chunk-level provenance** rather than model recall.

### Why versioning and citation storage are required

- The same question can have different correct answers across **versions** or **jurisdictions**. The **source_version** row is the anchor for “what text was in force.” **Chunks** and **citation anchors** tie user-visible quotes to immutable storage (version + offset or stable anchor key).

---

## 3. FOUNDATIONAL MODULE DESIGN

### `app/services/ingestion/`

- **parser:** Ingest raw files (PDF/HTML/text) → canonical extract (text + coarse structure). *Not implemented here.*
- **normalizer:** Unicode, whitespace, heading heuristics, pharmacy-specific boilerplate stripping (future).
- **chunker:** Deterministic splitting with stable ordinals and heading paths for citation.
- **metadata:** Authority, jurisdiction, effective dates, rule type—aligned with `regulation_source_versions` and chunk rows.

### `app/services/knowledge/`

- **source_registry:** CRUD-style operations over sources and versions (DB layer to be added when models exist).
- **versioning:** Supersedes chains, active vs retired, effective-date queries.
- **citations:** Stable citation keys and anchor JSON for UI and traces.
- **taxonomy:** Tags and many-to-many chunk tagging.

### `app/services/retrieval/`

- **lexical:** SQLite-friendly search first (FTS5 in a follow-on pass or external index).
- **embeddings:** Pluggable; store refs or blobs later—runtime DB is SQLite today (`app/db/session.py`).
- **hybrid:** Combine lexical + vector when embeddings exist.
- **reranker:** Thin interface for cross-encoder or LLM rerank—optional.

### `app/services/compliance/`

- **authority:** Map sources to issuing authority and trust tier.
- **effective_dates:** Resolve “active on date” and flag expired content.
- **conflicts:** Detect overlapping rules across versions/tags; surface for human review—not auto-merge.
- **escalation:** Hooks to require human approval or disclaimer when confidence is low.

### `app/services/assistant/`

- **orchestrator:** Later: assemble retrieval results into a **candidate evidence bundle** for the truth packet (does not replace `malone_service` entry).
- **formatter:** Citation-first answer formatting for the render layer.
- **guardrails:** Block delivery if citations missing or version ambiguous (policy to be tightened iteratively).

---

## 4. DATA MODEL RECOMMENDATION

Minimum entities (see `schemas/regulation_knowledge_v0.sql` and `tracking/reports/malone_regulation_schema_plan.md`):

| Entity | Purpose |
|--------|---------|
| **sources** | Logical document identity (stable key, title, type, authority, jurisdiction). |
| **source_versions** | Immutable snapshot per publish/revision; effective/superseded dates; storage checksum/URI; status. |
| **chunks** | Text segments with ordinal, heading path, rule type, plain-language summary, retrieval flags. |
| **citations** | Citation keys and anchor metadata linking chunks to display-safe references. |
| **taxonomy / tags** | Controlled vocabulary; **chunk_tags** many-to-many. |
| **ingestion_jobs** | Async/stage tracking, errors, linkage to a version. |
| **answer_traces** | Optional link to `malone_proposals.id`, chunk IDs used, verification outcome, model id—audit for compliance. |

Embeddings: defer to a dedicated store or blob column in a later pass; chunks carry `retrieval_ready` and optional `embedding_ref` for forward compatibility.

---

## 5. SELF-ASSEMBLING SYSTEM FIT

- New packages are **import-only** today: nothing in `app/main.py` or `malone_routes` imports them, so they impose **zero runtime cost** and **no behavior change**.
- On demand, **ingestion** can run as jobs writing SQL tables; **retrieval** modules can be called from a **future** `truth_packet_service` extension that adds an `evidence` section for regulation intents.
- **Assistant** orchestration stays **downstream** of deterministic retrieval results and **upstream** of the existing render verifier—preserving the current safety ordering.

---

## 6. IMPLEMENTATION ORDER

Next twelve steps (single-threaded; each is a shippable slice):

1. Apply **Alembic** `0002_regulation_knowledge_foundation` (or align SQLAlchemy models + autogenerate) on dev DB.
2. Add **SQLAlchemy models** for regulation tables under `app/models/` (small files; mirror migration).
3. Implement **source_registry** DB read APIs used by ingestion (create source + version rows).
4. Implement **ingestion job** lifecycle (queued → parsing → chunked → ready) with persistence.
5. Wire **parser** stub to real PDF/text library behind a feature flag (dependency in `requirements.txt`).
6. Implement **chunker** with deterministic tests (golden files in `tracking/` or `tests/`).
7. Add **lexical** search MVP (SQLite FTS or LIKE fallback) behind a service function.
8. Extend **truth_packet_service** with an optional `regulation_evidence` block *populated only* when retrieval returns hits (feature-flagged).
9. Add a **regulation intent** branch in `intent_service` (narrow, keyword or classifier) that does not change existing schedule flows.
10. Plumb **citations** into render input and **ProposalPanel** “sources” for internal chunks (parallel to web sources).
11. Add **compliance effective_dates** checks before answering (fail closed to clarification).
12. **Load testing / audit**: trace logging for answer_traces and review with `tracking/reports` checklist.

---

## 7. RISKS / BLOCKERS

- **SQLite vs vectors:** Current engine is SQLite (`runtime_v5.db`); native pgvector-style search is **not** available. Hybrid retrieval must use **lexical first**, then optional embeddings via stored blobs or a later Postgres migration—**repo-specific blocker** for “semantic-only” RAG.
- **Schema drift:** `Base.metadata.create_all` and Alembic can diverge if only one path is used; team must pick **Alembic as source of truth** for production.
- **Parallel roots:** `backend/`, `frontend/`, `dsos_replacements/` exist; **must not** duplicate regulation logic there—risk of forked behavior if someone edits passive lanes by mistake.
- **MaloneProposal JSON bundles:** Delivery fields may live partially in JSON on proposals; answer traces table should remain the **canonical** regulation audit row keyed by `proposal_id`.
- **Incomplete ORM:** `MaloneProposal` in `app/models/models.py` may not list every column the proposal service writes if migrations added columns not reflected in the model file—verify DB schema before adding FKs from `regulation_answer_traces` (SQLite pragma / live DB).
- **Workflow load:** Heavy ingestion should not block interactive Malone chat; run ingestion in **background tasks** or separate worker in a future pass.

---

## Appendix: Files added in this pass

See final summary in the thread response and `tracking/reports/malone_regulation_foundation_state.json`.
