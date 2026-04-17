# Arkansas family parser — before / after (Lawbook 2025-Dec-1)

## Snapshot: failing run (prior state)

From `tracking/reports/arkansas_handbook_ingest_validate_state.json` (2026-04-17 earlier run):

- `parsed_family_count`: **1**
- `reconciliation.toc_hits_found`: **0**
- `reconciliation.body_hits_found`: **1**
- Single family code **B** with spurious title from a **`B. (e) …`** line
- `retrieval_checks.skipped`: **true**
- `overall_status`: **FAIL** (`DB: family_count too low`)

## Snapshot: repair pass (same PDF)

From the re-run after parser repair (`stable_key` **ARK_ASBP_STATUTES_RULES_2025_12_DEC1_V2**):

- `parsed_family_count`: **8**
- `detection_layers.toc_trailing_letter`: **8**
- `handbook_body_anchor_char`: **10385** (replaces TOC-noise `statute_line_char` 413 for zoning)
- `title_validation.missing_codes`: **[]**
- `retrieval_checks.queries`: **5** probes with non-zero hits
- `overall_status`: **PASS**

## Structural takeaway

The **TOC and body headings in this PDF use different typography** than the older `A. Title` assumption. Recovering **A–H** requires **trailing-letter TOC parsing**, a **real body anchor**, and **title-phrase overrides** when the printed family letter is wrong.
