"""
Subsection-preserving segmentation for Arkansas-style numbering.

Role in Malone:
    Produces `subsection_path` strings for `legal_unit_chunks` (e.g. "(a)(1)(A)(i)").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Ordered: roman numeral words before single-letter (i) vs (1)
_TOKEN = re.compile(r"\(\d+\)|\([a-z]\)|\([A-Z]\)|\([ivxlcdm]+\)")

_PATH_LINE = re.compile(
    r"^\s*((?:\(\d+\)|\([a-z]\)|\([A-Z]\)|\([ivxlcdm]+\))+)\s*(.*)$",
)


@dataclass(frozen=True)
class SubsectionSegment:
    subsection_path: str
    body_text: str
    char_start: int | None
    char_end: int | None


def split_subsection_segments(unit_body: str, *, base_offset: int = 0) -> list[SubsectionSegment]:
    """
    Break a legal unit body into segments when lines begin with one or more (…) tokens.

    Continuation lines (no leading token) append to the current segment.
    """
    if not unit_body.strip():
        return [SubsectionSegment("", unit_body.strip() or "", None, None)]

    lines = unit_body.split("\n")
    segments: list[SubsectionSegment] = []
    current_path = ""
    buf: list[str] = []
    seg_start: int | None = None

    def flush() -> None:
        nonlocal buf, seg_start, current_path
        body = "\n".join(buf).strip()
        if not body and not current_path:
            buf = []
            seg_start = None
            return
        start = None if seg_start is None else base_offset + seg_start
        end = None if seg_start is None else base_offset + seg_start + len(body)
        segments.append(SubsectionSegment(current_path, body, start, end))
        buf = []
        seg_start = None

    for line in lines:
        stripped = line.lstrip()
        pl = _PATH_LINE.match(stripped)
        if pl:
            flush()
            tokens = pl.group(1)
            rest = pl.group(2)
            current_path = "".join(_TOKEN.findall(tokens))
            line_body = rest.strip()
            buf = [line_body] if line_body else []
            seg_start = unit_body.find(line) if line in unit_body else None
        else:
            if not buf and not stripped:
                continue
            if seg_start is None:
                seg_start = unit_body.find(line)
            buf.append(line.rstrip())

    flush()

    if not segments:
        return [SubsectionSegment("", unit_body.strip(), base_offset, base_offset + len(unit_body.strip()))]

    return segments
