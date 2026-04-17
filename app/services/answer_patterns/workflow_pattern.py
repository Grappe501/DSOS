"""Workflow / process-focused answer shape."""

from __future__ import annotations

from typing import Any

from app.services.answer_patterns import shared_formatting as sf
from app.services.decision_reasoning.fallback import should_emit_structured_sections


def render_legal(
    *,
    message: str,
    items: list[dict[str, Any]],
    normalized_bundle: dict[str, Any] | None,
    decision_workflow: dict[str, Any] | None,
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
        "Answer pattern: Workflow / process view (source-grounded; not legal advice).",
        "",
    ]
    sit = (message or "").strip()[:400]
    if sit:
        lines.append("Situation / question")
        lines.append(sit)
        lines.append("")

    if decision_workflow and should_emit_structured_sections(decision_workflow):
        steps = decision_workflow.get("action_steps") or []
        if steps:
            lines.append("Ordered steps (from normalized + evidence assembly)")
            for s in steps[:15]:
                summ = (s.get("summary") or "").strip()
                if not summ:
                    continue
                lines.append(f"  {s.get('order', '?')}. {summ[:900]}")
                if s.get("applies_to_role"):
                    lines.append(f"     Role hint: {s['applies_to_role']}")
            lines.append("")
        eses = decision_workflow.get("escalations") or []
        if eses:
            lines.append("When to stop or escalate")
            for e in eses[:8]:
                lines.append(f"  - [{e.get('kind')}] {str(e.get('text', ''))[:800]}")
            lines.append("")
    else:
        lines.append(
            "Process-oriented summary (partial — no complete workflow assembly available for this hit set)."
        )
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
    decision_workflow: dict[str, Any] | None,
    max_items: int,
    answer_title: str | None = None,
) -> str:
    title = answer_title or "Internal policy manual — reference only (not legal advice; confirm with policy owners)."
    norm = normalized_bundle or {}
    by_seg: dict[str, list[dict[str, Any]]] = norm.get("units_by_segment_id") or {}

    lines: list[str] = [title, "", "Answer pattern: Workflow / process view.", ""]
    sit = (message or "").strip()[:400]
    if sit:
        lines.append("Situation / question")
        lines.append(sit)
        lines.append("")

    if decision_workflow and should_emit_structured_sections(decision_workflow):
        steps = decision_workflow.get("action_steps") or []
        if steps:
            lines.append("Ordered steps")
            for s in steps[:15]:
                summ = (s.get("summary") or "").strip()
                if not summ:
                    continue
                lines.append(f"  {s.get('order', '?')}. {summ[:900]}")
            lines.append("")
        eses = decision_workflow.get("escalations") or []
        if eses:
            lines.append("Escalation / handoff")
            for e in eses[:8]:
                lines.append(f"  - {str(e.get('text', ''))[:800]}")
            lines.append("")
    else:
        lines.append("Process summary may be incomplete — see section excerpts below.")
        lines.append("")

    lines.append("Sources (sections and excerpts)")
    lines.append("")
    if not items:
        lines.append("No matching policy sections were found for this query.")
        return "\n".join(lines)

    lines.extend(sf.build_policy_items_section(items, by_seg=by_seg, max_items=max_items))
    lines.append("Confirm critical obligations with your policy administrator.")
    return "\n".join(lines)
