"""
Parse major handbook families (A–H) and optional embedded revision labels.

Role in Malone:
    Feeds `legal_document_families` rows (family_code, title, embedded_source_revision_label).

Arkansas ASBP (November 2025) uses:
    - TOC / front-matter lines listing ``A.`` … ``H.`` long titles
    - Body headings repeating those families before statute/rule blocks

This module prefers **body-slice** anchors (see ``family_boundary``) so the first
occurrence of a family heading inside the statutory body drives span starts; TOC
matches are used for provenance and confidence without discarding PDF grounding.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.services.legal_ingestion.family_boundary import (
    RawFamilyHit,
    find_statute_body_start,
    first_statute_line_char,
    reconcile_arkansas_family_hits,
    validate_against_expected_titles,
)

_FAMILY_LINE = re.compile(
    r"^\s*([A-H])[.)]\s+(.+?)\s*$",
    re.MULTILINE,
)

_EMBEDDED = re.compile(r"\(([^)]+)\)\s*$")


@dataclass(frozen=True)
class FamilySpan:
    family_code: str
    title: str
    embedded_revision: str | None
    char_start: int
    char_end: int
    span_provenance: str = "toc_family_v1"
    span_confidence: str = "medium"
    toc_char_start: int | None = None
    body_char_start: int | None = None
    reconciliation_notes: tuple[str, ...] = ()


def _extract_embedded_revision(title: str) -> tuple[str, str | None]:
    m = _EMBEDDED.search(title.strip())
    if not m:
        return title.strip(), None
    label = m.group(1).strip()
    base = title[: m.start()].strip()
    return base, label


def _legacy_merge_spans(text: str, spans: list[FamilySpan]) -> list[FamilySpan]:
    if not spans:
        return []
    spans_sorted = sorted(spans, key=lambda s: s.char_start)
    merged: list[FamilySpan] = []
    for i, span in enumerate(spans_sorted):
        end = spans_sorted[i + 1].char_start if i + 1 < len(spans_sorted) else len(text)
        merged.append(
            FamilySpan(
                family_code=span.family_code,
                title=span.title,
                embedded_revision=span.embedded_revision,
                char_start=span.char_start,
                char_end=end,
                span_provenance=span.span_provenance,
                span_confidence=span.span_confidence,
                toc_char_start=span.toc_char_start,
                body_char_start=span.body_char_start,
                reconciliation_notes=span.reconciliation_notes,
            )
        )
    return merged


def _legacy_parse_family_spans(text: str, *, min_title_len: int = 12) -> list[FamilySpan]:
    """Original whole-corpus A–H line heuristic (fallback)."""
    spans: list[FamilySpan] = []
    for m in _FAMILY_LINE.finditer(text):
        code = m.group(1).upper()
        raw_title = m.group(2).strip()
        if len(raw_title) < min_title_len:
            continue
        title, embedded = _extract_embedded_revision(raw_title)
        start = m.start()
        spans.append(
            FamilySpan(
                family_code=code,
                title=title,
                embedded_revision=embedded,
                char_start=start,
                char_end=len(text),
                span_provenance="legacy_full_corpus",
                span_confidence="low",
            )
        )
    return _legacy_merge_spans(text, spans)


def _parse_legacy_on_body_slice(text: str, body_start: int, *, min_title_len: int = 10) -> list[FamilySpan]:
    """Legacy matcher on ``text[body_start:]`` with offsets shifted (skips most TOC noise)."""
    slice_ = text[body_start:]
    spans: list[FamilySpan] = []
    for m in _FAMILY_LINE.finditer(slice_):
        code = m.group(1).upper()
        raw_title = m.group(2).strip()
        if len(raw_title) < min_title_len:
            continue
        title, embedded = _extract_embedded_revision(raw_title)
        start = body_start + m.start()
        spans.append(
            FamilySpan(
                family_code=code,
                title=title,
                embedded_revision=embedded,
                char_start=start,
                char_end=len(text),
                span_provenance="legacy_body_slice",
                span_confidence="medium",
            )
        )
    return _legacy_merge_spans(text, spans)


def _provenance_for_code(code: str, hit: RawFamilyHit, per_code: dict[str, Any]) -> tuple[str, str, tuple[str, ...]]:
    pc = per_code.get(code, {})
    note = str(pc.get("note", ""))
    notes_list: list[str] = []
    if note:
        notes_list.append(note)
    strat = pc.get("detection_strategy")
    if strat:
        notes_list.append(f"strategy={strat}")

    if hit.zone == "body":
        if "toc_char_start" in pc:
            prov = "toc_confirmed_by_body"
            conf = "high" if note == "body_after_toc" else "medium"
        else:
            prov = "body_only"
            conf = "medium"
    else:
        prov = "toc_only"
        conf = "low"
        notes_list.append("anchor_from_toc_zone_only")

    return prov, conf, tuple(notes_list)


def _finalize_from_reconciled(
    text: str,
    resolved: list[RawFamilyHit],
    notes: dict[str, Any],
) -> list[FamilySpan]:
    per_code = notes.get("per_code", {})
    n = len(text)
    by_code: dict[str, RawFamilyHit] = {}
    for h in sorted(resolved, key=lambda x: x.char_start):
        if h.family_code not in by_code:
            by_code[h.family_code] = h

    ordered = sorted(by_code.values(), key=lambda h: h.char_start)
    out: list[FamilySpan] = []
    for i, hit in enumerate(ordered):
        end = ordered[i + 1].char_start if i + 1 < len(ordered) else n
        code = hit.family_code
        prov, conf, rnotes = _provenance_for_code(code, hit, per_code)
        toc_c = per_code.get(code, {}).get("toc_char_start")
        body_c = per_code.get(code, {}).get("body_char_start")
        if hit.zone == "body":
            body_c = hit.char_start
        else:
            toc_c = hit.char_start
        out.append(
            FamilySpan(
                family_code=code,
                title=hit.title,
                embedded_revision=hit.embedded_revision,
                char_start=hit.char_start,
                char_end=end,
                span_provenance=prov,
                span_confidence=conf,
                toc_char_start=toc_c if isinstance(toc_c, int) else None,
                body_char_start=body_c if isinstance(body_c, int) else None,
                reconciliation_notes=rnotes,
            )
        )
    return out


def parse_family_spans(
    text: str,
    *,
    min_title_len: int = 12,
    page_map: Any | None = None,
) -> list[FamilySpan]:
    """
    Split full handbook text into spans between major A–H headings.

    When possible, uses ``family_boundary`` (body-first, TOC-informed). Falls back to
    legacy whole-corpus or body-slice heuristics if too few families are resolved.

    ``page_map`` is accepted for API compatibility with callers that already built a
    ``PageMap``; zone detection is primarily offset-based (statute line + TOC slice).
    """
    _ = page_map  # reserved for future page-aware TOC bounds
    body0 = find_statute_body_start(text)
    statute_pos = first_statute_line_char(text)
    resolved, notes = reconcile_arkansas_family_hits(
        text,
        body_start=body0,
        toc_min_title_len=8,
        body_min_title_len=10,
    )

    spans: list[FamilySpan] = []
    if len(resolved) >= 4:
        spans = _finalize_from_reconciled(text, resolved, notes)

    if len(spans) < 4:
        slice_start = body0 or 0
        if resolved and statute_pos is not None:
            slice_start = min(statute_pos, min(r.char_start for r in resolved))
        elif resolved:
            slice_start = min(slice_start, min(r.char_start for r in resolved))
        alt = _parse_legacy_on_body_slice(text, slice_start, min_title_len=10)
        if len(alt) > len(spans):
            spans = alt

    if not spans:
        spans = _legacy_parse_family_spans(text, min_title_len=min_title_len)

    return spans


def family_map_validation_report_payload(text: str) -> dict[str, Any]:
    """Machine-readable summary for tracking scripts (not legal advice)."""
    body0 = find_statute_body_start(text)
    resolved, notes = reconcile_arkansas_family_hits(text, body_start=body0)
    val = validate_against_expected_titles(resolved)
    return {
        "body_start_char": body0,
        "reconciliation": notes,
        "title_validation": val,
        "resolved_count": len(resolved),
    }
