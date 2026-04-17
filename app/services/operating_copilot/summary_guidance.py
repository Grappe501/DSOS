"""Short operating summary bullets (source-grounded, no new facts)."""

from __future__ import annotations

from typing import Any


def build_operating_summary_bullets(
    *,
    message: str,
    decision_workflow: dict[str, Any] | None,
    primary_scenario: str,
) -> list[str]:
    """3–6 bullets max; ties to decision_workflow fields only."""
    dw = decision_workflow or {}
    bullets: list[str] = []
    src = dw.get("sources_present") or []
    if src:
        bullets.append(f"Sources in scope: {', '.join(src)}.")
    roles = dw.get("roles") or []
    if roles:
        bullets.append(f"Roles mentioned in normalized fields: {len(roles)} group(s).")
    steps = dw.get("action_steps") or []
    if steps:
        bullets.append(f"Ordered steps available from evidence assembly: {len(steps)}.")
    esc = dw.get("escalations") or []
    if esc:
        bullets.append(f"Escalation/reporting cues present: {len(esc)}.")
    exc = dw.get("exceptions") or []
    if exc:
        bullets.append(f"Exception strings present: {len(exc)}.")
    if primary_scenario != "none":
        bullets.append(f"Scenario focus detected: {primary_scenario.replace('_', ' ')}.")
    if not bullets:
        bullets.append("Operational summary: rely on excerpts and citations above; no extra summary extracted.")
    return bullets[:6]
