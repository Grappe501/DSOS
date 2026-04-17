# Arkansas ASBP family parser — multi-strategy plan (December 2025 layout)

This note documents the **intentional layering** added for PDFs where:

- The **TOC lists statute cites** (`17-xx-xx`) so the **first cite is not the body start**.
- Major families appear as **`Long Title A`** (letter at **end** of line) rather than **`A. Long Title`**.

## Layer 1 — TOC / front matter

- Regex: title segment + whitespace + **`[A-H]`** at end of line (with length bounds).
- Skip: lines dominated by **`17-` statute ids**, “Continued” duplicates, and over-short fragments.
- Map letter to **canonical display title** for stable DB labels when the TOC line is truncated (notably **H**).

## Layer 2 — Body headings

- **`Letter` + space + title** (min length), excluding **`Letter` + `17-`** statute lines.
- **Filtered `Letter.` + title**: exclude subsection-style titles beginning with **`(e)`** etc.

## Layer 3 — Title phrases (Arkansas handbook)

- Normalize punctuation and spacing; longest / most specific phrases win.
- Overrides wrong printed letters (this PDF used **`F`** for **G** and **H** body headings).

## Layer 4 — Reconciliation

- Ordering **A→H**; **body start wins** for span anchoring when both TOC and body exist.
- Provenance: **`toc_confirmed_by_body`** when both anchors exist; strategies recorded per code.

## Layer 5 — Validation / reporting

- Reconciliation payload includes **`detection_layers`**, **`handbook_body_anchor_char`**, **`effective_zone_split_char`**, and per-code **`body_strategy` / `toc_strategy`**.
