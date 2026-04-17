"""Prerequisite phrases (line-anchored, explainable)."""

from __future__ import annotations

import re
from typing import Any

from app.services.workflow_extraction.sop_parser import split_lines

_HEAD = re.compile(r"(?i)^(prerequisites?|before (you )?begin|prior\s+to)\s*[:\-]?\s*(.*)$")


def extract_prerequisites(text: str) -> list[dict[str, Any]]:
    lines = split_lines(text or "")
    found: list[dict[str, Any]] = []
    buf: list[str] = []
    capture = False
    for ln in lines:
        m = _HEAD.match(ln)
        if m:
            capture = True
            rest = (m.group(2) or "").strip()
            if rest:
                buf.append(rest)
            continue
        if capture:
            if not ln.strip():
                break
            if re.match(r"(?i)^(step|\d+[\.\)])", ln):
                break
            buf.append(ln)
    if buf:
        blob = " ".join(buf).strip()
        if len(blob) >= 12:
            found.append({"prerequisite_text": blob[:1200], "source": "line_block_after_prerequisite_header"})
    return found[:5]
