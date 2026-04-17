"""Extract role / ownership lines from decision workflow."""

from __future__ import annotations

from typing import Any


def build_role_lines(decision_workflow: dict[str, Any] | None) -> list[str]:
    dw = decision_workflow or {}
    roles = dw.get("roles") or []
    lines: list[str] = []
    for r in roles[:15]:
        role = (r.get("role") or "").strip()
        if role:
            uids = r.get("unit_ids") or []
            tail = f" (normalized unit ids: {', '.join(uids[:4])})" if uids else ""
            lines.append(f"{role}{tail}")
    return lines
