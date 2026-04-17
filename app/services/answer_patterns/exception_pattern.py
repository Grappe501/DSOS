"""Exception / edge-case-focused answer shape."""

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
        "Answer pattern: Exceptions / special cases (source-grounded; not legal advice).",
        "",
    ]

    default_rule = sf.default_rule_text(units, items)
    lines.append("Default rule (from sources)")
    lines.append(default_rule or "See excerpts below — no single default line extracted.")
    lines.append("")

    excs = sf.collect_exception_texts(units)
    if excs:
        lines.append("Stated exceptions / carve-outs")
        for e in excs[:15]:
            lines.append(f"  - {e}")
        lines.append("")
    else:
        lines.append("Stated exceptions / carve-outs")
        lines.append("  (No explicit exception text in normalized fields for these hits.)")
        lines.append("")

    conds = sf.collect_condition_texts(units)
    if conds:
        lines.append("Conditions that may limit applicability")
        for c in conds[:12]:
            lines.append(f"  - {c}")
        lines.append("")

    lines.append("If unclear after reviewing excerpts, escalate to compliance or counsel.")
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

    lines: list[str] = [title, "", "Answer pattern: Exceptions / special cases.", ""]

    lines.append("Default rule")
    lines.append(sf.default_rule_text(units, items) or "See excerpts below.")
    lines.append("")

    excs = sf.collect_exception_texts(units)
    if excs:
        lines.append("Exceptions")
        for e in excs[:15]:
            lines.append(f"  - {e}")
        lines.append("")

    conds = sf.collect_condition_texts(units)
    if conds:
        lines.append("Conditions")
        for c in conds[:12]:
            lines.append(f"  - {c}")
        lines.append("")

    lines.append("If ambiguous, confirm with policy administration.")
    lines.append("")

    lines.append("Sources (sections and excerpts)")
    lines.append("")
    if not items:
        lines.append("No matching policy sections were found for this query.")
        return "\n".join(lines)

    lines.extend(sf.build_policy_items_section(items, by_seg=by_seg, max_items=max_items))
    lines.append("Confirm critical obligations with your policy administrator.")
    return "\n".join(lines)
