"""Simple conditional branches (if / unless / when)."""

from __future__ import annotations

import re
from typing import Any

_RE = re.compile(
    r"(?is)\b(if|unless|when|in the event that)\b[^.]{10,600}\.",
)


def extract_branches(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in _RE.finditer(text or ""):
        s = m.group(0).strip()
        out.append({"branch_condition_text": s[:900], "source": "regex_conditional"})
    return out[:10]
