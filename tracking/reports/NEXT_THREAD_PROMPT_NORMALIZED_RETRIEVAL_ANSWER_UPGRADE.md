# Next thread: normalized retrieval — follow-ups

## Completed

- Normalized units attach to legal and policy evidence bundles.
- Deterministic Malone answers include structured fields after citations/excerpts.
- Env flags: `MALONE_NORMALIZED_RETRIEVAL_ENABLED`, `MALONE_POLICY_EVIDENCE_ENABLED`, `MALONE_POLICY_LOOKUP_ENABLED`.

## Suggested next steps

1. **LLM path**: merge `normalized` summaries into `truth_packet` sections consumed by `render_conversational_response` with strict “do not contradict citations” instructions.
2. **UI**: optional `src/` panel showing normalized fields beside citations (still additive).
3. **Metrics**: log `normalized.fallback_reason` rates in `LegalAnswerTrace` meta or a new audit table.
4. **Ranking**: prefer `review_state=approved` when multiple units compete for the same chunk.

## Debug CLI

```bash
python tools/debug_normalized_retrieval.py --legal-source-version-id <UUID>
```

## Tests

```bash
python -m pytest tests/test_normalized_retrieval.py -q
```
