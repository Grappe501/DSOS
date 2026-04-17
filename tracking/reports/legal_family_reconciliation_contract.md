# Legal Family Reconciliation Contract (Arkansas ASBP Handbook)

## Goal

Produce one authoritative span per major family code (`A`–`H`) for persistence, using **transparent** deterministic rules when TOC listings and body headings disagree.

## Inputs

- Full linear corpus text.
- Classified hits from `family_boundary.reconcile_arkansas_family_hits`:
  - **TOC hit:** Major-family pattern before the first statute line **and** TOC-shaped line (dot leaders / contents banner).
  - **Body hit:** Major-family pattern at or after the first statute line, **or** before the first statute line **without** TOC shape.

## Per-code selection

1. If a **body** hit exists for code `X`, use it as the primary anchor for `X`.
2. Else if only a **TOC** hit exists for `X`, use it and mark provenance **`toc_only`** (low confidence).
3. Else code `X` is **missing** for this extract.

## Span construction

- Sort selected hits by `char_start` ascending.
- `char_end` = next hit’s `char_start`, or end of corpus.

## Provenance labels

| Label | Meaning |
|-------|---------|
| `toc_confirmed_by_body` | TOC and body anchors both present for the code. |
| `body_only` | Body anchor only. |
| `toc_only` | TOC anchor only (no body heading found for that code). |
| `legacy_full_corpus` / `legacy_body_slice` | Fallback parser path; treat as lower structural trust. |

## Confidence

- **high:** `toc_confirmed_by_body` with consistent ordering (implementation may emit **medium** when positions are unusual; see persisted `span_confidence`).
- **medium:** `body_only` or reconciled primary path without full confirmation.
- **low:** `toc_only` or legacy fallbacks.

## Non-goals

- Does not decide legal meaning or amend source text.
- Does not replace citation or page-grounding contracts.
