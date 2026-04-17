"""Escalation / notify / compliance handoff triggers."""

from __future__ import annotations

import re
from typing import Any

_RE = re.compile(
    r"(?is)\b(escalat(?:e|ion)|notify\s+(?:the\s+)?(?:pharmacist|supervisor|compliance|management)|"
    r"contact\s+(?:compliance|legal)|report\s+to)\b[^.]{5,500}\.",
)


def extract_escalation_triggers(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in _RE.finditer(text or ""):
        s = m.group(0).strip()
        out.append({"escalation_trigger_text": s[:900], "source": "regex_escalation"})
    return out[:10]
