"""Extract ordered steps from numbered lists and bullets (inspectable regex)."""

from __future__ import annotations

import re
from typing import Any


_RE_NUMBERED = re.compile(
    r"^\s*(?P<n>\d{1,3})[\.\)]\s+(?P<body>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_RE_BULLET = re.compile(r"^\s*[-*•]\s+(?P<body>.+?)\s*$", re.MULTILINE)


def extract_numbered_steps(text: str) -> list[dict[str, Any]]:
    """Explicit 1. 2. or 1) style steps."""
    out: list[dict[str, Any]] = []
    for m in _RE_NUMBERED.finditer(text or ""):
        body = (m.group("body") or "").strip()
        if len(body) < 3:
            continue
        out.append(
            {
                "step_order": int(m.group("n")),
                "step_label": body[:200],
                "step_description": body[:1200],
                "source": "regex_numbered_list",
            }
        )
    out.sort(key=lambda x: (x.get("step_order") or 999))
    return out


def extract_bullet_steps(text: str, *, max_steps: int = 12) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, m in enumerate(_RE_BULLET.finditer(text or "")):
        if i >= max_steps:
            break
        body = (m.group("body") or "").strip()
        if len(body) < 4:
            continue
        out.append(
            {
                "step_order": i + 1,
                "step_label": body[:200],
                "step_description": body[:1200],
                "source": "regex_bullet_list",
            }
        )
    return out
