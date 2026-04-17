"""
Detect statute-style and board-rule units inside a family text span.

Role in Malone:
    Populates `legal_units` with `unit_kind` + `primary_citation` + heading text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_STATUTE = re.compile(
    r"^\s*(\d{1,3}-\d{1,3}-\d{1,4})\s*(?:[.—\-]\s*)?(.*)$",
    re.MULTILINE,
)

_RULE_ROMAN = re.compile(
    r"^\s*Section\s+([IVXLCDM]+)\b[.:]?\s*(.*)$",
    re.IGNORECASE | re.MULTILINE,
)

_PDMP = re.compile(
    r"^\s*(PDMP\s+Section\s+([IVXLCDM]+))\b[.:]?\s*(.*)$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class LegalUnitSpan:
    unit_kind: str
    primary_citation: str | None
    heading_raw: str | None
    char_start: int
    char_end: int
    body_text: str
    body_global_char_start: int


def _heading_for_statute(line_rest: str) -> str | None:
    h = line_rest.strip()
    return h if h else None


def find_legal_units_in_span(family_text: str, *, base_offset: int = 0) -> list[LegalUnitSpan]:
    markers: list[tuple[int, str, str | None, str | None]] = []

    for m in _STATUTE.finditer(family_text):
        cite = m.group(1)
        rest = m.group(2) or ""
        markers.append((m.start(), "statute_section", cite, _heading_for_statute(rest)))

    for m in _RULE_ROMAN.finditer(family_text):
        roman = m.group(1).upper()
        rest = m.group(2) or ""
        markers.append((m.start(), "rule_section", f"Section {roman}", _heading_for_statute(rest)))

    for m in _PDMP.finditer(family_text):
        roman = m.group(2).upper()
        rest = m.group(3) or ""
        markers.append((m.start(), "pdmp_section", f"PDMP Section {roman}", _heading_for_statute(rest)))

    markers.sort(key=lambda t: t[0])
    units: list[LegalUnitSpan] = []
    for i, (start, kind, cite, heading) in enumerate(markers):
        end = markers[i + 1][0] if i + 1 < len(markers) else len(family_text)
        body = family_text[start:end]
        lines = body.split("\n", 1)
        if len(lines) > 1:
            body_only = lines[1].lstrip("\n")
            body_start_local = start + len(lines[0]) + 1
        else:
            body_only = ""
            body_start_local = start + len(lines[0])
        body_global = base_offset + body_start_local
        units.append(
            LegalUnitSpan(
                unit_kind=kind,
                primary_citation=cite,
                heading_raw=heading,
                char_start=base_offset + start,
                char_end=base_offset + end,
                body_text=body_only.strip(),
                body_global_char_start=body_global,
            )
        )
    return units
