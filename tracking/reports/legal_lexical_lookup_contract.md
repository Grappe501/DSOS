# Legal Lexical Lookup Contract

## Corpus

- **Primary store:** `legal_unit_chunks.body_text` joined to `legal_units` and `legal_document_families`.
- **Citation store:** `legal_citations` (`citation_key`, `normalized_citation`, `anchor_json`).

## Lexical search (`search_legal_chunks_lexical`)

- **Method:** SQLite `ILIKE` substring match (case-insensitive).
- **Fields searched:** chunk body, citation key, normalized citation, unit `heading_raw`, family `title`.
- **Result shape:** `{ legal_unit_chunk_id, citation_key, snippet, family_code, family_title, subsection_path, primary_citation }`.

## Citation lookup (`find_chunks_by_citation_text`)

- Normalize query with `normalize_statute_like_citation` (strip internal whitespace).
- Match `legal_citations.normalized_citation` OR raw equality fallbacks.

## Title / family phrase lookup

- `find_chunks_by_section_title` — `heading_raw` ILIKE.
- `find_chunks_by_family_and_phrase` — family title ILIKE AND chunk body ILIKE.

## Hybrid (`retrieve_legal_evidence_bundle`)

- Returns lexical hits only; `embedding_leg: disabled` until embeddings exist.

## Future extensions

- FTS5 token index for ranking.
- Filter by `legal_source_version_id` to avoid cross-version collisions in dev.
