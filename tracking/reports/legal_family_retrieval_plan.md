# Legal Family Retrieval Plan (Scoping + Confidence)

## Problem

Family-aware retrieval must not treat **TOC-only** or **legacy** family boundaries as strongly as **body-confirmed** bands when answering or assembling evidence.

## Mechanisms

1. **`legal_source_version_id`** (existing) — scopes chunks to one ingest snapshot (see `legal_retrieval_scoping_plan.md`).
2. **`family_code` filter** (this pass) — `search_legal_chunks_lexical` and `find_chunks_by_family_and_phrase` can restrict to one letter band.
3. **`min_family_span_confidence`** — optional filter on `legal_document_families.meta_json` → `family_map.span_confidence` (`high` / `medium` / `low`), implemented via post-filter with over-fetch for small limits.
4. **Hit payload** — `family_span_confidence` is surfaced on lexical hits when present.

## Caller guidance

- Always pass **`legal_source_version_id`** for production-style queries.
- When using **`family_code`**, prefer also passing **`min_family_span_confidence="medium"`** or **`"high"`** if the UI promises “inside family X” semantics.
- If **`min_family_span_confidence`** returns few rows, widen confidence or fall back to version-scoped search without family structure (chunk text remains page-grounded).

## Not implemented here

- Vector / embedding family routing.
- Automatic downgrade of user-facing messaging (callers should use confidence to adjust copy).
