"""Role ownership hints from explicit terms (no hallucinated job titles)."""

from __future__ import annotations

import re
from typing import Any

_ROLE_TERMS = (
    ("pharmacist", re.compile(r"\b(pharmacist|RPh|registered pharmacist|staff pharmacist)\b", re.I)),
    ("pharmacy_technician", re.compile(r"\b(pharmacy technician|CPhT|technician)\b", re.I)),
    ("pic", re.compile(r"\b(PIC|pharmacist[- ]in[- ]charge)\b", re.I)),
    ("nurse", re.compile(r"\b(RN|LPN|nurse|nursing staff)\b", re.I)),
    ("compliance", re.compile(r"\b(compliance officer|compliance department)\b", re.I)),
)


def extract_role_owners(text: str) -> list[dict[str, Any]]:
    t = text or ""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for label, rx in _ROLE_TERMS:
        if rx.search(t) and label not in seen:
            seen.add(label)
            m = rx.search(t)
            span = m.group(0) if m else label
            out.append({"role_key": label, "evidence_span": span[:200], "source": "regex_role_term"})
    return out
