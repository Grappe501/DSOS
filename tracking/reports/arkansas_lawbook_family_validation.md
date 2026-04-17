# Arkansas Law Book — Family Validation Report

**Date:** 2026-04-16  
**Method:** Deterministic comparison of expected visible A–H partitions (November 2025 compilation) against `parse_family_spans` / `family_map_validation_report_payload` output.

## Expected structure (ground-truth target)

The compilation’s front matter / TOC presents major partitions including:

- **A** — Pharmacy Practice Act  
- **B** — Miscellaneous Statutes Related to Pharmacy  
- **C** — Uniform Controlled Substances Act  
- **D** — Insurance Policies – Prescription Drug Benefits  
- **E** — Food, Drug, and Cosmetic Act  
- **F** — Controlled Substances and Legend Drugs  
- **G** — Administrative Procedure Act  
- **H** — Rules Pertaining to Arkansas Prescription Drug Monitoring Program  

## Deterministic checks in code

- `family_boundary.ARKANSAS_EXPECTED_FAMILY_TITLES` — short phrase allowlist per code for title validation (not legal classification).
- `validate_against_expected_titles` — reports `missing_codes` and `title_mismatch_codes` for a hit list.

## Fixture run (CI-friendly)

**Source:** `tracking/fixtures/arkansas_handbook_vertical_slice_sample.txt`  

**Result:** Two families detected (**A**, **H**), matching the excerpt (it does not contain B–G bodies). Title phrases for A and H match the allowlist.

**Command:**

`python tracking/scripts/family_map_validate.py --fixture tracking/fixtures/arkansas_handbook_vertical_slice_sample.txt`

## Full PDF run (operator)

Run against the uploaded November 2025 PDF on a workstation with the file available:

`python tracking/scripts/family_map_validate.py --pdf "<path-to-pdf>"`

Compare JSON `families[]` to the expected table above; inspect `validation.title_validation` for mismatches.

## Interpretation

- **Missing codes** in validation usually mean the extract does not contain those headings at sufficient title length, or layout broke line-based regexes.
- **Title mismatch** flags codes whose detected title does not contain any allowlisted phrase (tune phrases before loosening regex).
