"""Collect role / actor hints from normalized units (pass-through, no inference beyond grouping)."""

from __future__ import annotations

from typing import Any


def collect_roles(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Distinct applies_to_role values with unit ids for traceability."""
    by_role: dict[str, list[str]] = {}
    for u in units:
        r = (u.get("applies_to_role") or "").strip()
        if not r:
            continue
        uid = str(u.get("id") or "")
        by_role.setdefault(r, []).append(uid)
    return [{"role": k, "unit_ids": sorted(set(v))} for k, v in sorted(by_role.items())]
