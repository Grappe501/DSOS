"""Group condition strings from units (no free-form evaluation of user-specific facts)."""

from __future__ import annotations

from typing import Any


def group_conditions(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for u in units:
        t = (u.get("condition_text") or "").strip()
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(
            {
                "text": t[:2000],
                "unit_id": u.get("id"),
                "normalized_unit_type": u.get("normalized_unit_type"),
                "source_type": u.get("source_type"),
            }
        )
    return out
