# Next thread: Arkansas family parser — follow-ups

## Completed in the last pass

- Multi-strategy **A–H** recovery for **Lawbook 2025-Dec-1** (TOC trailing letters + body anchors + title overrides).
- **Retrieval QA** runs after successful ingest even when other non-retrieval checks fail.
- **`stable_citation_key`** includes **`legal_unit_id`** to avoid duplicate keys when multiple parsed units share the same primary citation under multi-family spans.

## Suggested next work (optional)

1. **Edition robustness**: If a future PDF omits `\nA Pharmacy Practice Act\n`, add fallback body anchors (e.g. first `Pharmacy Practice Act` edition line + following body heading) without hardcoding page numbers.
2. **Reduce noise in `body_letter_space` hit counts**: tighten filters if a new edition introduces more false `Letter Title` lines.
3. **Golden fixtures**: Add a trimmed text fixture checked into `tracking/fixtures/` representing this TOC + one body page for CI.
4. **Monitor chunk counts**: Family splits change unit/chunk cardinality versus the old single-family span; confirm downstream UX still performs acceptably.

## Re-run command (reference)

```bash
python tracking/scripts/run_arkansas_handbook_ingest_validate.py --pdf "tracking/data/arkansas_handbook/Lawbook-2025-Dec-1.pdf" --stable-key "ARK_ASBP_STATUTES_RULES_2025_12_DEC1_V2" --version-label "Lawbook 2025-Dec-1 V2"
```

Use a **new `--stable-key`** whenever the database already contains the prior key.
