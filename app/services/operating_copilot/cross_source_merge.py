"""Summarize legal / policy / SOP bundle presence for the copilot (no duplicate ORM logic)."""

from __future__ import annotations

from typing import Any


def evidence_scope_summary(
    *,
    legal_bundle: dict[str, Any] | None,
    policy_bundle: dict[str, Any] | None,
    sop_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    """Inspectable counts for truth packet / copilot block."""
    out: dict[str, Any] = {"source_types_with_items": [], "item_counts": {}}
    for label, bundle in (("legal_handbook", legal_bundle), ("policy_manual", policy_bundle), ("sop_workflow", sop_bundle)):
        if not bundle or not bundle.get("enabled"):
            continue
        n = len(bundle.get("items") or [])
        out["item_counts"][label] = n
        if n > 0:
            out["source_types_with_items"].append(label)
    out["cross_source"] = len(out["source_types_with_items"]) > 1
    return out
