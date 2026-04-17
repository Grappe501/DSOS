# Next Thread — After Phase 3 (Retrieval)

## Completed

- Lexical and citation retrieval dedupe + deterministic ordering.

## Next: Phase 4 — Legal Evidence Integration

- Wire `build_legal_evidence_bundle` + `enrich_truth_packet_with_legal` on the Malone path (feature-flagged).
- Disable web search for `legal_handbook` intent in truth packet rules.

## Flags

- `MALONE_LEGAL_EVIDENCE_ENABLED` — enable bundle + intent routing for handbook queries.
