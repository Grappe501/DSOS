"""Checkpoint / verification language."""

from __future__ import annotations

import re
from typing import Any

_RE = re.compile(
    r"(?is)\b(verify|confirm|check(?:point)?|ensure|validate|document that|sign off)\b[^.]{0,200}\.",
)


def extract_checkpoints(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in _RE.finditer(text or ""):
        s = m.group(0).strip()
        if len(s) > 20:
            out.append({"checkpoint_text": s[:900], "source": "regex_checkpoint_verification"})
    return out[:8]
