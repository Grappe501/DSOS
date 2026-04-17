"""Requirement-focused answer shape (legal + policy)."""

from __future__ import annotations

from typing import Any

from app.services.answer_patterns import shared_formatting as sf


def render_legal(
    *,
    message: str,
    items: list[dict[str, Any]],
    normalized_bundle: dict[str, Any] | None,
    max_items: int,
) -> str:
    norm = normalized_bundle or {}
    by_chunk: dict[str, list[dict[str, Any]]] = norm.get("units_by_chunk_id") or {}
    units: list[dict[str, Any]] = []
    for lst in by_chunk.values():
        units.extend(lst)

    lines: list[str] = [
        "Arkansas State Board of Pharmacy handbook — internal reference (not legal advice)",
        "",
        "Answer pattern: Requirement / obligation view (source-grounded; not legal advice).",
        "",
    ]
    if norm.get("enabled") and by_chunk:
        lines.append(
            "Structured fields below use normalized knowledge labels where available; verify against excerpts."
        )
        lines.append("")

    lines.append("Bottom line")
    lines.append(sf.bottom_line_from_units_or_items(units, items))
    lines.append("")

    roles = sf.collect_roles(units)
    if roles:
        lines.append("Who must act / applies to")
        for r in roles[:20]:
            lines.append(f"  - {r}")
        lines.append("")

    rlevels = sf.collect_requirement_levels(units)
    if rlevels:
        lines.append("Requirement strength (from normalized fields)")
        for rl in rlevels:
            lines.append(f"  - {rl}")
        lines.append("")

    conds = sf.collect_condition_texts(units)
    if conds:
        lines.append("Conditions")
        for c in conds[:12]:
            lines.append(f"  - {c}")
        lines.append("")

    excs = sf.collect_exception_texts(units)
    if excs:
        lines.append("Exceptions (if stated)")
        for e in excs[:12]:
            lines.append(f"  - {e}")
        lines.append("")

    rep = sf.collect_reporting_texts(units)
    if rep:
        lines.append("Documentation / reporting / escalation cues")
        for r in rep[:10]:
            lines.append(f"  - {r}")
        lines.append("")

    lines.append("Sources (citations and excerpts)")
    lines.append("")
    if not items:
        lines.append("No matching excerpts were found in the ingested compilation for this query.")
        return "\n".join(lines)

    lines.extend(sf.build_legal_items_section(items, by_chunk=by_chunk, max_items=max_items))
    lines.append(
        "Verify against your official compilation or primary legal resources. "
        "This tool summarizes ingested text only."
    )
    return "\n".join(lines)


def render_policy(
    *,
    message: str,
    items: list[dict[str, Any]],
    normalized_bundle: dict[str, Any] | None,
    max_items: int,
    answer_title: str | None = None,
) -> str:
    title = answer_title or "Internal policy manual — reference only (not legal advice; confirm with policy owners)."
    norm = normalized_bundle or {}
    by_seg: dict[str, list[dict[str, Any]]] = norm.get("units_by_segment_id") or {}
    units: list[dict[str, Any]] = []
    for lst in by_seg.values():
        units.extend(lst)

    lines: list[str] = [title, "", "Answer pattern: Requirement / obligation view.", ""]
    if norm.get("enabled") and by_seg:
        lines.append("Structured fields use normalized labels where available; verify against excerpts.")
        lines.append("")

    lines.append("Bottom line")
    lines.append(sf.bottom_line_from_units_or_items(units, items))
    lines.append("")

    roles = sf.collect_roles(units)
    if roles:
        lines.append("Who the rule applies to")
        for r in roles[:20]:
            lines.append(f"  - {r}")
        lines.append("")

    rlevels = sf.collect_requirement_levels(units)
    if rlevels:
        lines.append("Requirement strength")
        for rl in rlevels:
            lines.append(f"  - {rl}")
        lines.append("")

    conds = sf.collect_condition_texts(units)
    if conds:
        lines.append("Conditions")
        for c in conds[:12]:
            lines.append(f"  - {c}")
        lines.append("")

    excs = sf.collect_exception_texts(units)
    if excs:
        lines.append("Exceptions")
        for e in excs[:12]:
            lines.append(f"  - {e}")
        lines.append("")

    rep = sf.collect_reporting_texts(units)
    if rep:
        lines.append("Reporting / escalation")
        for r in rep[:10]:
            lines.append(f"  - {r}")
        lines.append("")

    lines.append("Sources (sections and excerpts)")
    lines.append("")
    if not items:
        lines.append("No matching policy sections were found for this query.")
        return "\n".join(lines)

    lines.extend(sf.build_policy_items_section(items, by_seg=by_seg, max_items=max_items))
    lines.append("Confirm critical obligations with your policy administrator.")
    return "\n".join(lines)
