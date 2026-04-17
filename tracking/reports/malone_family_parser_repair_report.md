# Malone Arkansas family parser repair (December 2025 lawbook)

## 1. WHAT FAILED BEFORE

- The December 2025 PDF’s **Table of Contents does not use** the legacy pattern `A. Title` on its own line. It uses **`Title … A`** (family letter **after** the title) and statute cite lists that include `17-xx-xx` **before** the real body, so the first `17-xx-xx` match was **not** a reliable “body starts here” marker.
- **TOC hits were effectively zero** (`toc_hits_found: 0`) because TOC rows were not classified as TOC zone and no trailing-letter matcher existed.
- **Body hits collapsed** to a single bad anchor: a nested list line like `B. (e) The Prescription Drug Monitoring Program…` was mistaken for **Family B**, producing **one** `legacy_body_slice` span and **title validation failure** (`family_count` too low → **OVERALL FAIL**).
- **Retrieval QA did not run** (`retrieval_checks.skipped: true`) because the runner required `not failures` while **DB family_count** added a failure—an avoidable gate unrelated to retrieval health.

## 2. WHAT THIS PASS CHANGED

- **`family_boundary.py`**: Added a **handbook body anchor** (`\nA Pharmacy Practice Act\n`) so TOC statute lists no longer define the body boundary; added **TOC trailing-letter** detection (`Title … B`); added **body `Letter Title`** detection; filtered **nested `(e)`** false positives on `Letter.` headings; added **title-phrase reconciliation** (fixes OCR/layout drift such as **`F Administrative Procedure Act` → G** and **`F Rules … PDMP` → H**); merged strategies with explicit per-code notes.
- **`toc_parser.py`**: Appends **`strategy=…`** into reconciliation notes when present in reconciliation payload.
- **`run_arkansas_handbook_ingest_validate.py`**: Runs **retrieval probes whenever ingest completes**, without requiring an empty failure list (weak family map must not block retrieval QA).
- **`citations.py` + `arkansas_pipeline.py`**: Included **`legal_unit_id`** in the `stable_citation_key` hash payload so **duplicate primary citations across distinct parsed units** (exposed once families split cleanly) do not violate `legal_citations.citation_key` uniqueness.

## 3. MULTI-STRATEGY FAMILY DETECTION NOW USED

1. **TOC / front matter — trailing family letter** (`toc_trailing_letter`): lines like `Miscellaneous Statutes Related to Pharmacy B`, skipping “Continued” rows and statute-number noise lines.
2. **Body — letter + space + title** (`body_letter_space_title`): lines like `B Miscellaneous Statutes Related to Pharmacy`.
3. **Body — dot headings with filters** (`body_dot_heading` / `toc_dot_heading`): classic `A. Title`, excluding subsection markers like `(e) …`.
4. **Title phrase reconciliation** (`title_override`): normalized phrase map assigns **A–H** when the printed letter is wrong; surfaced as `body_letter_space_title_title_override` for G/H in this PDF.
5. **Reconciliation**: Per code **A→H**, prefer **body** start when present, retain **TOC** offsets for provenance; strategy `reconciled_toc_body` when both exist.

## 4. REAL PDF RE-RUN RESULT

- **Command**:  
  `python tracking/scripts/run_arkansas_handbook_ingest_validate.py --pdf "tracking/data/arkansas_handbook/Lawbook-2025-Dec-1.pdf" --stable-key "ARK_ASBP_STATUTES_RULES_2025_12_DEC1_V2" --version-label "Lawbook 2025-Dec-1 V2"`
- **Parsed families**: **8** (A–H), **title checks pass**, **`toc_trailing_letter`: 8** hits in reconciliation payload.
- **Ingest**: **completed**, **8** `legal_document_families`, **6289** chunks / citations (page-grounded).
- **Runner**: **PASS** (see `tracking/reports/arkansas_handbook_ingest_validate_state.json`).

## 5. BEFORE / AFTER FAMILY COMPARISON

| Aspect | Before | After |
|--------|--------|--------|
| Families detected | 1 (spurious B) | **8** (A–H) |
| TOC layer | 0 hits | **8** trailing-letter anchors |
| Body anchor | First `17-xx-xx` at char 413 (TOC noise) | **`A Pharmacy Practice Act` at char 10385** |
| Provenance | `legacy_body_slice` | **`toc_confirmed_by_body`** with high/medium confidence |
| Title validation | Missing A,C–H; B mismatch | **All codes present; no mismatches** |

## 6. RETRIEVAL QA STATUS

- **Before**: `queries: []`, `skipped: true` (gated on failures).
- **After**: **5 probes executed** (3 citation lookups + 2 lexical phrase queries), all **scoped to the ingested source version** with non-zero hits. See `retrieval_checks` in `arkansas_handbook_ingest_validate_state.json`.

## 7. OVERALL OUTCOME

- **Goal met for this pass**: **Eight** handbook families recovered with **materially sensible spans** and **PASS** on the one-command runner; retrieval QA is **meaningful** again.
- **Residual risk**: Other ASBP PDF editions may use slightly different body headings; the **handbook body anchor** and **title map** may need extension if a future edition drops `A Pharmacy Practice Act` as the first body heading.

## 8. HARD-FAIL COMPLIANCE CHECK

- **No edits** under `backend/`, `frontend/`, or `dsos_replacements/`.
- **Ingestion pipeline** was not rewritten; changes are **family boundary / TOC logic**, a **small retrieval gate**, and a **targeted citation_key disambiguation** required for successful multi-family persistence.
- **Real PDF** ingest/validate was **re-run**; outputs written under `tracking/reports/`.
- **Remaining issues** are **reported** here (not hidden); optional follow-ups include broader edition coverage for **body anchor** fallbacks.
