"""Group escalation triggers and reporting duties (from normalized escalation_text / output_outcome)."""

from __future__ import annotations

from typing import Any


def group_escalations(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for u in units:
        for key, label in (("escalation_text", "escalation"), ("output_outcome_text", "reporting_or_outcome")):
            t = (u.get(key) or "").strip()
            if not t:
                continue
            sig = f"{label}:{t}"
            if sig in seen:
                continue
            seen.add(sig)
            out.append(
                {
                    "kind": label,
                    "text": t[:2000],
                    "unit_id": u.get("id"),
                    "source_type": u.get("source_type"),
                }
            )
    return out
