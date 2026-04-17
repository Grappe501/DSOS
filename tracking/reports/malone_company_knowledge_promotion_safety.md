# Company Knowledge Promotion — Safety

## Precedence

1. **Source text and legal units** remain authoritative for what was ingested.
2. **Human review** adjusts trust labels and operational readiness (retrieval, staging), not the evidentiary text.
3. **Governance hints** in API responses are labeled read-only and carry an explicit precedence note.

## Guards

- `assert_no_source_text_mutation_fields` on review `meta_json`.
- Activation default requires review head `approved` before `promote-version`.
- Append-only review events preserve history for rejected and superseded paths.

## Non-goals

- No silent mass promotion of all internal sources.
- No parallel “Malone admin CMS” — all flows go through existing review + ingestion control services.
