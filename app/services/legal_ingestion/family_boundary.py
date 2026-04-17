"""
Deterministic Arkansas handbook major-family (A–H) boundary detection.

Purpose:
    Split the linear corpus into family spans using body-first anchors, with TOC
    matches used for provenance / confidence — without replacing PageMap or PDF extraction.

Role in Malone:
    Called from ``toc_parser.parse_family_spans`` so ``arkansas_pipeline`` persists
    trustworthy ``legal_document_families`` rows (structure band, not legal advice).

Design:
    1. Locate approximate start of statutory body (first Arkansas-style statute id line).
    2. Collect ``A.`` / ``B.`` … ``H.`` heading lines in the body slice (primary truth for span starts).
    3. Collect TOC-zone headings before the body start (for confirmation and page-span notes).
    4. Reconcile per code with transparent rules; merge adjacent spans for persistence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# First line that looks like an Arkansas compiled statute cite (body text, not cover noise).
_STATUTE_LINE = re.compile(r"(?m)^\s*(\d{1,3}-\d{1,3}-\d{1,4})\b")

# Major family heading: letter, '.' or ')', rest of line is title.
_FAMILY_HEAD = re.compile(
    r"(?m)^\s*([A-H])[.)]\s+(.+?)\s*$",
)

_EMBEDDED = re.compile(r"\(([^)]+)\)\s*$")

# Typical TOC row: title + dot leaders + page number (PDF extraction may vary spacing).
_TOC_DOT_LEADERS = re.compile(r"\.{3,}.*\d+\s*$")

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


def find_statute_body_start(text: str) -> int | None:
    """
    Approximate start of the statutory body for zone profiling.

    Prefer the first statute line; if missing in long corpora, fall back to a conservative
    fraction so front matter is skipped. (Family reconciliation uses ``first_statute_line_char``
    plus TOC-vs-body line shape — see ``reconcile_arkansas_family_hits``.)
    """
    m_stat = _STATUTE_LINE.search(text)
    if m_stat:
        return m_stat.start()
    n = len(text)
    if n > 80_000:
        return min(n // 12, 120_000)
    return None


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


def _hits_in_range(
    text: str,
    start: int,
    end: int,
    *,
    min_title_len: int,
    statute_pos: int | None,
) -> list[RawFamilyHit]:
    out: list[RawFamilyHit] = []
    slice_ = text[start:end]
    for m in _FAMILY_HEAD.finditer(slice_):
        raw_title = (m.group(2) or "").strip()
        if len(raw_title) < min_title_len:
            continue
        code = m.group(1).upper()
        title, emb = _extract_embedded_revision(raw_title)
        abs_start = start + m.start()
        z = _zone_for_family_hit(text, abs_start, statute_pos)
        out.append(
            RawFamilyHit(
                family_code=code,
                title=title,
                embedded_revision=emb,
                char_start=abs_start,
                zone=z,
            )
        )
    return out


def _first_hit_per_code(hits: list[RawFamilyHit]) -> dict[str, RawFamilyHit]:
    by_code: dict[str, RawFamilyHit] = {}
    ordered = sorted(hits, key=lambda h: h.char_start)
    for h in ordered:
        if h.family_code not in by_code:
            by_code[h.family_code] = h
    return by_code


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
    Build per-code anchors from TOC zone + body zone and return reconciliation diagnostics.

    Zone assignment uses ``first_statute_line_char`` plus line-shape (TOC dot leaders vs body
    headings). ``body_start`` is retained for diagnostics only (legacy callers).

    Returns:
        ordered body hits to become family spans (one per code when found), and a dict of notes.
    """
    n = len(text)
    statute_pos = first_statute_line_char(text)
    toc_hits = _hits_in_range(
        text, 0, n, min_title_len=toc_min_title_len, statute_pos=statute_pos
    )
    toc_hits = [h for h in toc_hits if h.zone == "toc"]
    body_hits = _hits_in_range(
        text, 0, n, min_title_len=body_min_title_len, statute_pos=statute_pos
    )
    body_hits = [h for h in body_hits if h.zone == "body"]

    toc_by = _first_hit_per_code(toc_hits)
    body_by = _first_hit_per_code(body_hits)

    notes: dict[str, Any] = {
        "body_start_char": body_start,
        "statute_line_char": statute_pos,
        "toc_hits_found": len(toc_hits),
        "body_hits_found": len(body_hits),
        "per_code": {},
    }

    resolved: list[RawFamilyHit] = []
    for code in "ABCDEFGH":
        b = body_by.get(code)
        t = toc_by.get(code)
        pc: dict[str, Any] = {}
        if b and t:
            pc["toc_char_start"] = t.char_start
            pc["body_char_start"] = b.char_start
            if b.char_start >= t.char_start:
                pc["note"] = "body_after_toc"
            else:
                pc["note"] = "body_before_toc_unexpected"
        elif b:
            pc["body_char_start"] = b.char_start
            pc["note"] = "body_only"
        elif t:
            pc["toc_char_start"] = t.char_start
            pc["note"] = "toc_only_no_body_heading"
        else:
            pc["note"] = "missing"
        notes["per_code"][code] = pc

        chosen = b or t
        if chosen:
            resolved.append(chosen)

    resolved.sort(key=lambda h: h.char_start)
    return resolved, notes


def validate_against_expected_titles(hits: list[RawFamilyHit]) -> dict[str, Any]:
    """Compare detected titles to the Arkansas November 2025 visible partition phrases."""
    seen = _first_hit_per_code(hits)
    missing = [c for c in "ABCDEFGH" if c not in seen]
    title_mismatch = [c for c, h in seen.items() if not _title_matches_expected(c, h.title)]
    return {
        "expected_codes": list("ABCDEFGH"),
        "detected_codes": sorted(seen.keys()),
        "missing_codes": missing,
        "title_mismatch_codes": title_mismatch,
    }
