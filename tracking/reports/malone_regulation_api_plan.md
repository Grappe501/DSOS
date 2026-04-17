# Malone Regulation API Plan (Design Note — Not Implemented)

**Status:** Foundation pass only; **no new routes** were added. This document defines a compatible future surface for FastAPI under the existing `/api` namespace and JWT/RBAC patterns (`app/api/deps.py`).

## Principles

1. **Read-heavy first:** ingest and index are admin/operator flows; pharmacists query through Malone or read-only regulation endpoints.
2. **Role gates:** align with existing roles (`owner`, `admin`, `scheduler`, `viewer`); **writes** restricted to `owner`/`admin` unless expanded later.
3. **No bypass of Malone safety:** user-facing Q&A should still produce a **proposal + truth packet + verification** when routed through `POST /api/malone/chat`; dedicated regulation endpoints are optional for internal tools/tests.

## Proposed endpoints (future)

### Registry (admin)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/regulation/sources` | List sources with filters (jurisdiction, type). |
| `POST` | `/api/regulation/sources` | Register logical source (`stable_key`, title, authority). |
| `GET` | `/api/regulation/sources/{source_id}/versions` | List versions for a source. |
| `POST` | `/api/regulation/sources/{source_id}/versions` | Create version row (metadata before file upload). |

### Ingestion (admin / worker token)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/regulation/ingestions` | Start ingestion job (`source_version_id`, storage hint). |
| `GET` | `/api/regulation/ingestions/{job_id}` | Job status for UI polling. |

### Retrieval (internal or Malone-only)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/regulation/search` | Lexical/hybrid search returning chunk IDs + snippets + citation keys. |

**Recommendation:** Prefer **not** exposing `search` publicly until citations and effective-date compliance checks are enforced in the service layer; keep search internal and let `malone_service` call `retrieval.hybrid` as a library.

### Traces (admin / audit)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/regulation/traces` | List answer traces with filters (date, proposal_id). |

## Request/response shapes (sketch)

- **Search:** `{ "query": str, "jurisdiction": str | null, "as_of_date": date | null, "limit": int }`  
  → `{ "hits": [ { "chunk_id", "citation_key", "snippet", "source_version_id" } ] }`

## Frontend

- **No change in this pass.** Future: optional `MalonePage` mode or separate `Regulation` page calling the same Malone chat with a `scope` field once backend supports intent scoping—**assumption:** add optional `message_metadata` later rather than breaking `maloneApi.chat`.

## Compatibility

- Matches existing JSON APIs and `src/lib/api.js` auth header pattern.
- Does not require WebSockets for v0 ingestion polling.
