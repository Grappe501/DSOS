"""Stop / do-not-proceed conditions."""

from __future__ import annotations

import re
from typing import Any

_RE = re.compile(
    r"(?is)\b(do not (?:proceed|continue)|stop (?:if|when)|halt|cease|must not (?:proceed|continue)|"
    r"discontinue if|abort if)\b[^.]{10,500}\.",
)


def extract_stop_conditions(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in _RE.finditer(text or ""):
        s = m.group(0).strip()
        out.append({"stop_condition_text": s[:900], "source": "regex_stop_condition"})
    return out[:8]
