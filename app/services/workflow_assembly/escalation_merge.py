"""Bridge normalized escalations with extracted escalation triggers (dedupe by text prefix)."""

from __future__ import annotations

from typing import Any


def merge_escalation_views(
    normalized_escalations: list[dict[str, Any]],
    action_steps: list[dict[str, Any]],
) -> list[str]:
    seen: set[str] = set()
    lines: list[str] = []
    for e in normalized_escalations or []:
        txt = (e.get("text") or "").strip()
        if txt and txt[:80] not in seen:
            seen.add(txt[:80])
            lines.append(f"[normalized] {txt[:900]}")
    for s in action_steps:
        ex = s.get("workflow_extraction") or {}
        for et in ex.get("escalation_triggers") or []:
            txt = (et.get("escalation_trigger_text") or "").strip()
            if txt and txt[:80] not in seen:
                seen.add(txt[:80])
                lines.append(f"[text_signal] {txt[:900]}")
    return lines[:25]
