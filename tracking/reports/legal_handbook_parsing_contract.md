# Legal Handbook Parsing Contract (Arkansas ASBP Compilation)

## Inputs

- **Normalized UTF-8 text** (`normalize_extracted_text` applied).
- Optional manifest: `stable_key`, `version_label`, `compiled_publication_date`, checksum, `storage_uri`.

## Outputs (in-memory → DB)

### Families

- **Detector:** lines matching `^([A-H])[.)]\s+{title}` with title length ≥ 12 characters (reduces TOC false positives).
- **Fields:** `family_code`, `title`, optional `embedded_source_revision_label` parsed from trailing `(Label)`.

### Legal units (per family text span)

| `unit_kind` | Start pattern |
|-------------|----------------|
| `statute_section` | `^\s*\d{1,3}-\d{1,3}-\d{1,4}\b` |
| `rule_section` | `^\s*Section\s+([IVXLCDM]+)` |
| `pdmp_section` | `^\s*PDMP\s+Section\s+([IVXLCDM]+)` |
| `family_body` | Fallback when no unit headers match in span |

First line of each unit is stripped from `body_text`; remainder feeds subsection parsing.

### Subsection segments

- **New segment** when a line begins with one or more parenthesis tokens: digit, lowercase letter, uppercase letter, or Roman numeral letters inside parentheses.
- **Continuation** lines belong to the current segment until the next subsection leader line.
- **`subsection_path`:** concatenation of tokens on the leader line (e.g. `(b)(1)`).

## Warnings / limits

- OCR noise may break family or unit regexes; operators should fix text or adjust heuristics.
- Duplicate headings in TOC vs body may create duplicate family candidates if title-length filter is insufficient.
