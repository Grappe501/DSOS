# Malone Legal Retrieval & Citation Plan

## Objectives

- Answer questions like: “What does **17-92-115** require?”, “Is this **statute** or **board rule**?”, “Which **family (A–H)** is this from?”, “What **page** in the November 2025 compiled PDF?”
- Keep **deterministic citation** as the primary retrieval key; semantic search is additive, not authoritative.

## Retrieval stack (order of application)

1. **`citation_lookup`:** If the user message contains a normalized statute/rule key, resolve directly via `legal_citations.citation_key` → chunk(s).
2. **`lexical`:** FTS / keyword over `legal_unit_chunks.body_text` with filters.
3. **`hybrid`:** Merge lexical with embedding scores when `embedding_ref` exists.
4. **`reranker`:** Boost exact citation match, heading match, and same-family continuity.
5. **`authority_filter`:** Restrict to `authority_type` when the question asks “statute only” or “rules only”.

## Evidence bundle (for truth packets)

Each hit should return:

- `chunk_id`
- `citation_key` + human-readable citation
- `authority_type`
- `family_code` + family title (via join)
- `subsection_path`
- `anchor_json.page` (and char span if available)
- Short **verbatim** excerpt (from chunk body; no summarization in retrieval)

## Tracing

- On Malone proposal `p`, insert **`legal_answer_traces`** with:
  - `chunk_ids_json`
  - `citation_keys_json`
  - `verified` (after render verifier acknowledges grounding)
  - `meta_json` with retrieval diagnostics

## Malone integration (later)

- Extend **`build_truth_packet`** with optional `internal_legal_evidence` and `forbidden_claims` additions from `legal_assistant/guardrails.py`.
- Do **not** bypass **`verify_rendered_response`** for user-visible legal answers.

## Non-goals

- Web search as authority for Arkansas pharmacy law when internal chunks exist.
- LLM-generated citations not present in `legal_citations`.
