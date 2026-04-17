"""
Deterministic Arkansas handbook major-family (A–H) boundary detection.

Purpose:
    Split the linear corpus into family spans using body-first anchors, with TOC
    matches used for provenance / confidence — without replacing PageMap or PDF extraction.

Role in Malone:
    Called from ``toc_parser.parse_family_spans`` so ``arkansas_pipeline`` persists
    trustworthy ``legal_document_families`` rows (structure band, not legal advice).

Design:
    1. Locate handbook body anchor (e.g. first ``A Pharmacy Practice Act`` body heading) when present;
       avoid treating the first ``17-xx-xx`` in the TOC as the body boundary.
    2. Collect TOC rows with **trailing** family letters (``Title … B``) and body ``Letter Title`` headings.
    3. Keep filtered ``Letter.`` headings for older layouts; reconcile with title-phrase map when letters drift.
    4. Reconcile per code with transparent rules; merge adjacent spans for persistence.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

# First line that looks like an Arkansas compiled statute cite (body text, not cover noise).
_STATUTE_LINE = re.compile(r"(?m)^\s*(\d{1,3}-\d{1,3}-\d{1,4})\b")

# Major family heading: letter, '.' or ')', rest of line is title.
_FAMILY_HEAD = re.compile(
    r"(?m)^\s*([A-H])[.)]\s+(.+?)\s*$",
)

# December 2025 (and similar) body layout: single letter, space, long title (not "A. ...").
_BODY_LETTER_SPACE_TITLE = re.compile(
    r"(?m)^\s*([A-H])\s+(.{15,320})\s*$",
)

# TOC row where the family code is a trailing letter (not "A. Title"): "… Title A"
_TOC_TRAILING_FAMILY_LETTER = re.compile(
    r"(?m)^(.{12,260}?)\s+([A-H])\s*$",
)

_EMBEDDED = re.compile(r"\(([^)]+)\)\s*$")

# Typical TOC row: title + dot leaders + page number (PDF extraction may vary spacing).
_TOC_DOT_LEADERS = re.compile(r"\.{3,}.*\d+\s*$")

# Display titles aligned with the ASBP handbook compilation (used when extraction truncates).
ARKANSAS_CANONICAL_FAMILY_TITLES: dict[str, str] = {
    "A": "Pharmacy Practice Act",
    "B": "Miscellaneous Statutes Related to Pharmacy",
    "C": "Uniform Controlled Substances Act",
    "D": "Insurance Policies – Prescription Drug Benefits",
    "E": "Food, Drug, and Cosmetic Act",
    "F": "Controlled Substances and Legend Drugs",
    "G": "Administrative Procedure Act",
    "H": "Rules Pertaining to Arkansas Prescription Drug Monitoring Program",
}

# Longest phrase first — title inference for body/TOC lines with OCR or letter drift.
_TITLE_PHRASE_TO_CODE: list[tuple[str, str]] = [
    ("rules pertaining to arkansas prescription drug monitoring program", "H"),
    ("administrative procedure act", "G"),
    ("controlled substances and legend drugs", "F"),
    ("food drug and cosmetic act", "E"),
    ("insurance policies", "D"),
    ("prescription drug benefits", "D"),
    ("uniform controlled substances act", "C"),
    ("miscellaneous statutes related to pharmacy", "B"),
    ("pharmacy practice act", "A"),
]

# Canonical short phrases for validation (November 2025 Arkansas ASBP compilation).
ARKANSAS_EXPECTED_FAMILY_TITLES: dict[str, tuple[str, ...]] = {
    "A": ("Pharmacy Practice Act",),
    "B": ("Miscellaneous Statutes", "Miscellaneous Statutes Related to Pharmacy"),
    "C": ("Uniform Controlled Substances",),
    "D": ("Insurance Policies", "Prescription Drug Benefits"),
    "E": ("Food, Drug, and Cosmetic", "Food, Drug"),
    "F": ("Controlled Substances and Legend", "Legend Drugs"),
    "G": ("Administrative Procedure Act",),
    "H": (
        "Prescription Drug Monitoring",
        "Rules Pertaining to Arkansas Prescription Drug Monitoring",
        "Monitoring Program",
    ),
}


@dataclass(frozen=True)
class RawFamilyHit:
    family_code: str
    title: str
    embedded_revision: str | None
    char_start: int
    zone: str  # "toc" | "body"
    detection_strategy: str | None = None


def _extract_embedded_revision(title: str) -> tuple[str, str | None]:
    m = _EMBEDDED.search(title.strip())
    if not m:
        return title.strip(), None
    label = m.group(1).strip()
    base = title[: m.start()].strip()
    return base, label


def first_statute_line_char(text: str) -> int | None:
    """Character offset of the first statute-cite line (used to separate TOC rows from body)."""
    m = _STATUTE_LINE.search(text)
    return m.start() if m else None


def handbook_body_anchor_char(text: str) -> int | None:
    """
    Start of the compiled statute *body* for Arkansas ASBP lawbooks whose TOC lists cites
    before the real body (so the first ``17-xx-xx`` match is not a reliable body boundary).

    Prefers the first ``A Pharmacy Practice Act`` body heading line used in recent PDFs.
    """
    for needle in ("\nA Pharmacy Practice Act\n", "\nA Pharmacy Practice Act\r\n", "A Pharmacy Practice Act\n"):
        i = text.find(needle)
        if i >= 0:
            return i
    m = re.search(
        r"(?m)^Pharmacy Practice Act\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*$",
        text,
    )
    return m.start() if m else None


def find_statute_body_start(text: str) -> int | None:
    """
    Approximate start of the statutory body for zone profiling.

    Prefer a handbook body anchor when present; else the first statute line; else a conservative
    fraction for long corpora.
    """
    anchor = handbook_body_anchor_char(text)
    if anchor is not None:
        return anchor
    m_stat = _STATUTE_LINE.search(text)
    if m_stat:
        return m_stat.start()
    n = len(text)
    if n > 80_000:
        return min(n // 12, 120_000)
    return None


def _normalize_title_match_blob(title: str) -> str:
    t = unicodedata.normalize("NFKC", title).lower()
    t = re.sub(r"[\u2013\u2014\u2212\-]", " ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def infer_family_code_from_title(title: str) -> str | None:
    """Map a heading string to A–H using normalized known phrases (longest / most specific first)."""
    norm = _normalize_title_match_blob(title)
    if not norm:
        return None
    # D needs both insurance + benefits when possible; single phrase can mis-fire — check pair first.
    if "insurance policies" in norm and "prescription drug benefits" in norm:
        return "D"
    for phrase, code in _TITLE_PHRASE_TO_CODE:
        if phrase in norm:
            if phrase == "prescription drug benefits" and code == "D":
                if "insurance" not in norm:
                    continue
            if phrase == "insurance policies" and code == "D":
                if "prescription" not in norm and "benefits" not in norm:
                    continue
            return code
    return None


def _is_nested_list_letter_heading(title: str) -> bool:
    """Reject ``B. (e) The …`` subsection lines mistaken for Family B."""
    t = title.strip()
    return bool(re.match(r"^\([a-zA-Z]{1,3}\)\s", t))


def _is_statute_toc_or_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if re.match(r"^\d{1,3}-\d{1,3}-\d{1,4}\b", s):
        return True
    if re.match(r"^(?:Section|Definitions|Designation)\b", s, re.I):
        return False
    return False


def _is_toc_trailing_noise_title(title_part: str) -> bool:
    s = title_part.strip()
    if len(s) < 12:
        return True
    if _is_statute_toc_or_noise_line(s):
        return True
    return False


def _toc_trailing_letter_hits(
    text: str,
    toc_zone_end: int,
) -> list[RawFamilyHit]:
    """Layer 1: TOC lines like ``Miscellaneous Statutes Related to Pharmacy B`` (title + trailing code)."""
    out: list[RawFamilyHit] = []
    slice_ = text[:toc_zone_end]
    for m in _TOC_TRAILING_FAMILY_LETTER.finditer(slice_):
        title_part = (m.group(1) or "").strip()
        code = m.group(2).upper()
        if _is_toc_trailing_noise_title(title_part):
            continue
        if re.search(r"(?i)\bcontinued\b", title_part):
            continue
        abs_start = m.start()
        title = ARKANSAS_CANONICAL_FAMILY_TITLES.get(code, title_part)
        out.append(
            RawFamilyHit(
                family_code=code,
                title=title,
                embedded_revision=None,
                char_start=abs_start,
                zone="toc",
                detection_strategy="toc_trailing_letter",
            )
        )
    return out


def _body_letter_space_hits(
    text: str,
    body_zone_start: int,
    *,
    statute_split: int | None,
) -> list[RawFamilyHit]:
    """Layer 2: ``B Miscellaneous Statutes Related to Pharmacy`` (letter + space + title)."""
    out: list[RawFamilyHit] = []
    slice_ = text[body_zone_start:]
    for m in _BODY_LETTER_SPACE_TITLE.finditer(slice_):
        letter = m.group(1).upper()
        raw_title = (m.group(2) or "").strip()
        if raw_title.startswith("17-"):
            continue
        if len(raw_title) < 15:
            continue
        inferred = infer_family_code_from_title(raw_title)
        code = inferred or letter
        title = ARKANSAS_CANONICAL_FAMILY_TITLES.get(code, raw_title)
        abs_start = body_zone_start + m.start()
        z = _zone_for_family_hit(text, abs_start, statute_split)
        strat = "body_letter_space_title"
        if inferred and inferred != letter:
            strat = "body_letter_space_title_title_override"
        out.append(
            RawFamilyHit(
                family_code=code,
                title=title,
                embedded_revision=None,
                char_start=abs_start,
                zone=z,
                detection_strategy=strat,
            )
        )
    return out


def _family_dot_heading_hits_filtered(
    text: str,
    *,
    min_title_len: int,
    statute_split: int | None,
) -> list[RawFamilyHit]:
    """Layer 2b: ``A. Title`` lines, excluding nested list markers like ``B. (e)``."""
    out: list[RawFamilyHit] = []
    for m in _FAMILY_HEAD.finditer(text):
        raw_title = (m.group(2) or "").strip()
        if len(raw_title) < min_title_len:
            continue
        if _is_nested_list_letter_heading(raw_title):
            continue
        letter = m.group(1).upper()
        inferred = infer_family_code_from_title(raw_title)
        code = inferred or letter
        title, emb = _extract_embedded_revision(raw_title)
        if inferred and inferred != letter:
            title = ARKANSAS_CANONICAL_FAMILY_TITLES.get(code, title)
        abs_start = m.start()
        z = _zone_for_family_hit(text, abs_start, statute_split)
        strat = "body_dot_heading" if z == "body" else "toc_dot_heading"
        if inferred and inferred != letter:
            strat = strat + "_title_override"
        out.append(
            RawFamilyHit(
                family_code=code,
                title=title,
                embedded_revision=emb,
                char_start=abs_start,
                zone=z,
                detection_strategy=strat,
            )
        )
    return out


def _merge_hits_first_per_code(hits: list[RawFamilyHit]) -> dict[str, RawFamilyHit]:
    by_code: dict[str, RawFamilyHit] = {}
    ordered = sorted(hits, key=lambda h: h.char_start)
    for h in ordered:
        if h.family_code not in by_code:
            by_code[h.family_code] = h
    return by_code


def _line_at_index(text: str, char_idx: int) -> str:
    if char_idx < 0 or char_idx >= len(text):
        return ""
    line_start = text.rfind("\n", 0, char_idx) + 1
    line_end = text.find("\n", char_idx)
    if line_end < 0:
        line_end = len(text)
    return text[line_start:line_end]


def _is_toc_style_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if _TOC_DOT_LEADERS.search(s):
        return True
    if re.search(r"(?i)\btable\s+of\s+contents\b", s):
        return True
    return False


def _zone_for_family_hit(text: str, char_start: int, statute_pos: int | None) -> str:
    """
    ``toc`` = TOC-style row before the first statute line; ``body`` otherwise.

    A major-family heading that appears *before* the first statute line but **without**
    TOC dot-leaders is treated as **body** (cover blocks can mirror real headings).
    """
    sp = statute_pos if statute_pos is not None else len(text)
    if char_start >= sp:
        return "body"
    line = _line_at_index(text, char_start)
    if _is_toc_style_line(line):
        return "toc"
    return "body"


def _title_matches_expected(code: str, title: str) -> bool:
    t = title.lower()
    for phrase in ARKANSAS_EXPECTED_FAMILY_TITLES.get(code, ()):
        if phrase.lower() in t:
            return True
    return False


def reconcile_arkansas_family_hits(
    text: str,
    *,
    body_start: int | None,
    toc_min_title_len: int = 8,
    body_min_title_len: int = 10,
) -> tuple[list[RawFamilyHit], dict[str, Any]]:
    """
    Multi-strategy family anchors: TOC trailing letters, body ``Letter Title`` headings,
    filtered ``Letter.`` headings, plus title-phrase reconciliation when letters drift.

    ``body_start`` is diagnostic; zone split prefers ``handbook_body_anchor_char`` over the
    first raw ``17-xx-xx`` line (TOC lists cites in many PDFs).
    """
    _ = toc_min_title_len
    n = len(text)
    statute_pos = first_statute_line_char(text)
    anchor = handbook_body_anchor_char(text)
    effective_split = anchor or statute_pos

    toc_zone_end = anchor if anchor is not None else (statute_pos if statute_pos is not None else min(n, 100_000))

    toc_trailing = _toc_trailing_letter_hits(text, toc_zone_end)
    # When no ``A Pharmacy Practice Act`` anchor (fixtures), scan from 0 so headings above the
    # first statute line are not skipped; real PDFs set ``anchor`` so TOC noise is excluded.
    body_scan_start = anchor if anchor is not None else 0
    letter_space = _body_letter_space_hits(text, body_scan_start, statute_split=effective_split)
    dot_all = _family_dot_heading_hits_filtered(
        text,
        min_title_len=body_min_title_len,
        statute_split=effective_split,
    )
    legacy_toc_dots = [h for h in dot_all if h.zone == "toc" and h.char_start < toc_zone_end]
    legacy_body_dots = [h for h in dot_all if h.zone == "body"]

    toc_pool = toc_trailing + legacy_toc_dots
    body_pool = letter_space + legacy_body_dots

    toc_by = _merge_hits_first_per_code(toc_pool)
    body_by = _merge_hits_first_per_code(body_pool)

    notes: dict[str, Any] = {
        "body_start_char": body_start,
        "handbook_body_anchor_char": anchor,
        "statute_line_char": statute_pos,
        "effective_zone_split_char": effective_split,
        "toc_zone_end_char": toc_zone_end,
        "toc_hits_found": len(toc_pool),
        "body_hits_found": len(body_pool),
        "detection_layers": {
            "toc_trailing_letter": len(toc_trailing),
            "body_letter_space": len(letter_space),
            "dot_heading_all": len(dot_all),
        },
        "per_code": {},
    }

    resolved: list[RawFamilyHit] = []
    for code in "ABCDEFGH":
        b = body_by.get(code)
        t = toc_by.get(code)
        pc: dict[str, Any] = {}
        if b:
            pc["body_char_start"] = b.char_start
            pc["body_strategy"] = b.detection_strategy
        if t:
            pc["toc_char_start"] = t.char_start
            pc["toc_strategy"] = t.detection_strategy
        if b and t:
            if b.char_start >= t.char_start:
                pc["note"] = "body_after_toc"
            else:
                pc["note"] = "body_before_toc_unexpected"
        elif b:
            pc["note"] = "body_only"
        elif t:
            pc["note"] = "toc_only_no_body_heading"
        else:
            pc["note"] = "missing"
        if b and t:
            pc["detection_strategy"] = "reconciled_toc_body"
        elif b:
            pc["detection_strategy"] = b.detection_strategy or "body_only"
        elif t:
            pc["detection_strategy"] = t.detection_strategy or "toc_only"
        notes["per_code"][code] = pc

        chosen = b or t
        if chosen:
            resolved.append(chosen)

    resolved.sort(key=lambda h: h.char_start)
    return resolved, notes


def validate_against_expected_titles(hits: list[RawFamilyHit]) -> dict[str, Any]:
    """Compare detected titles to the Arkansas November 2025 visible partition phrases."""
    seen = _merge_hits_first_per_code(hits)
    missing = [c for c in "ABCDEFGH" if c not in seen]
    title_mismatch = [c for c, h in seen.items() if not _title_matches_expected(c, h.title)]
    return {
        "expected_codes": list("ABCDEFGH"),
        "detected_codes": sorted(seen.keys()),
        "missing_codes": missing,
        "title_mismatch_codes": title_mismatch,
    }
