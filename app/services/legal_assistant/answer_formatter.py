"""
Purpose:
    Format answers with required anchors: citation key, family title,
    subsection path, page anchor.

Role in Malone:
    Ensures user-visible strings remain tied to persisted handbook rows.

Expected inputs:
    Evidence items from ``legal_evidence_service.build_legal_evidence_bundle``.

Expected outputs:
    Plain text blocks suitable for deterministic Malone delivery.
"""

from __future__ import annotations

from typing import Any

from app.services.decision_reasoning.fallback import should_emit_structured_sections


def _fmt_pages(item: dict[str, Any]) -> str:
    ps = item.get("page_start")
    pe = item.get("page_end")
    if ps is None and pe is None:
        return "unknown"
    if pe is None or pe == ps:
        return str(ps)
    return f"{ps}–{pe}"


def _append_normalized_lines(lines: list[str], nu: dict[str, Any], prefix: str) -> None:
    """Add optional structured fields (additive; does not replace citations)."""
    t = nu.get("normalized_unit_type")
    if t:
        lines.append(f"   {prefix}Type: {t}")
    rl = nu.get("requirement_level")
    if rl:
        lines.append(f"   {prefix}Requirement level: {rl}")
    at = nu.get("applies_to_role")
    if at:
        lines.append(f"   {prefix}Applies to (role): {at}")
    act = nu.get("action_type")
    if act:
        lines.append(f"   {prefix}Action: {act}")
    for label, key in (
        ("Summary", "plain_language_summary"),
        ("Condition", "condition_text"),
        ("Exception", "exception_text"),
        ("Escalation", "escalation_text"),
    ):
        val = nu.get(key)
        if val and str(val).strip():
            lines.append(f"   {prefix}{label}: {str(val).strip()[:900]}")
    conf = nu.get("confidence_level")
    rev = nu.get("review_state")
    if conf or rev:
        lines.append(f"   {prefix}Normalization meta: confidence={conf or '—'}, review={rev or '—'}")
    if nu.get("caveat"):
        lines.append(f"   {prefix}(Heuristic label — verify against excerpt and official sources.)")


def _append_decision_workflow_sections(lines: list[str], decision_workflow: dict[str, Any] | None) -> None:
    """Append structured operational guidance after citation-first body (additive)."""
    if not decision_workflow or not should_emit_structured_sections(decision_workflow):
        return
    lines.append("")
    lines.append("--- Operational guidance (structured from normalized units; verify against excerpts above) ---")
    oi = decision_workflow.get("operational_intent")
    if oi:
        lines.append(f"Focus: {oi.replace('_', ' ')}")
    if decision_workflow.get("caution_low_trust_dominant"):
        lines.append(
            "Caution: many matching units are draft or low-confidence — treat steps as non-authoritative until reviewed."
        )
    if decision_workflow.get("partial_workflow") and decision_workflow.get("partial_workflow_reason"):
        lines.append(
            f"Partial workflow signal: {decision_workflow['partial_workflow_reason']} — not a complete procedure from sources alone."
        )
    src = decision_workflow.get("sources_present") or []
    if src:
        lines.append(f"Sources represented: {', '.join(src)}")

    roles = decision_workflow.get("roles") or []
    if roles:
        lines.append("")
        lines.append("Who may be involved (from normalized fields):")
        for r in roles[:12]:
            lines.append(f"  - {r.get('role')}")

    steps = decision_workflow.get("action_steps") or []
    if steps:
        lines.append("")
        lines.append("Ordered steps / actions (source-derived):")
        for s in steps[:15]:
            summ = (s.get("summary") or "").strip()
            if not summ:
                continue
            lines.append(f"  {s.get('order', '?')}. {summ[:900]}")
            if s.get("applies_to_role"):
                lines.append(f"     Role hint: {s['applies_to_role']}")

    conds = decision_workflow.get("conditions") or []
    if conds:
        lines.append("")
        lines.append("Conditions (when this may apply):")
        for c in conds[:10]:
            lines.append(f"  - {str(c.get('text', ''))[:900]}")

    excs = decision_workflow.get("exceptions") or []
    if excs:
        lines.append("")
        lines.append("Exceptions / overrides:")
        for e in excs[:10]:
            lines.append(f"  - {str(e.get('text', ''))[:900]}")

    eses = decision_workflow.get("escalations") or []
    if eses:
        lines.append("")
        lines.append("Escalation / reporting:")
        for e in eses[:10]:
            lines.append(f"  - [{e.get('kind')}] {str(e.get('text', ''))[:900]}")

    lines.append("")
    lines.append(
        "This section organizes normalized fields only; it is not independent legal or policy advice."
    )


def append_decision_workflow_lines(lines: list[str], decision_workflow: dict[str, Any] | None) -> None:
    """Public alias for the pattern layer (same behavior as the legacy helper)."""
    _append_decision_workflow_sections(lines, decision_workflow)


def format_legal_lookup_answer_standard(
    items: list[dict[str, Any]],
    *,
    max_items: int = 6,
    normalized_bundle: dict[str, Any] | None = None,
) -> str:
    """
    Legacy single-shape legal answer (citation-first). Does not append decision/workflow
    (the smart-pattern integration adds that uniformly).
    """
    lines: list[str] = [
        "Arkansas State Board of Pharmacy handbook — internal reference (not legal advice)",
        "",
    ]
    norm = normalized_bundle or {}
    by_chunk: dict[str, list[dict[str, Any]]] = norm.get("units_by_chunk_id") or {}
    if norm.get("enabled") and by_chunk:
        lines.append(
            "Structured fields below are heuristic labels from normalized knowledge units; "
            "they do not replace the citation-backed excerpts."
        )
        lines.append("")

    if not items:
        lines.append(
            "No matching excerpts were found in the ingested compilation for this query. "
            "Try a statute-style citation (for example a section number), a shorter phrase, "
            "or confirm the handbook ingest completed for this environment."
        )
        return "\n".join(lines)

    for i, it in enumerate(items[:max_items], start=1):
        cite = it.get("citation_key") or it.get("primary_citation") or "—"
        fam = it.get("family_title") or it.get("family_code") or ""
        head = it.get("heading_raw")
        path = it.get("subsection_path")
        lines.append(f"{i}. Citation: {cite}")
        if fam:
            lines.append(f"   Family: {fam}")
        if head:
            lines.append(f"   Heading: {head}")
        if path:
            lines.append(f"   Subsection path: {path}")
        lines.append(f"   Pages: {_fmt_pages(it)}")
        snip = (it.get("snippet") or "").strip()
        if snip:
            lines.append(f"   Excerpt: {snip}")

        cid = str(it.get("legal_unit_chunk_id") or "")
        if cid and cid in by_chunk:
            for j, nu in enumerate(by_chunk[cid][:2], start=1):
                lines.append(f"   Normalized ({j}):")
                _append_normalized_lines(lines, nu, prefix="")

        lines.append("")

    lines.append(
        "Verify against your official compilation or primary legal resources. "
        "This tool summarizes ingested text only."
    )
    return "\n".join(lines)


def format_legal_lookup_answer(
    items: list[dict[str, Any]],
    *,
    max_items: int = 6,
    normalized_bundle: dict[str, Any] | None = None,
    decision_workflow: dict[str, Any] | None = None,
    message: str | None = None,
    truth_packet: dict[str, Any] | None = None,
) -> str:
    """
    Citation-first, inspectable text. Not a substitute for official sources.

    When ``message`` is provided, applies smart answer patterns (deterministic) then appends
    decision/workflow sections when enabled.
    """
    if (message or "").strip():
        from app.services.answer_patterns.integration import render_legal_smart_answer

        return render_legal_smart_answer(
            message=message or "",
            items=items,
            normalized_bundle=normalized_bundle,
            decision_workflow=decision_workflow,
            max_items=max_items,
            truth_packet=truth_packet,
        )
    lines = format_legal_lookup_answer_standard(
        items, max_items=max_items, normalized_bundle=normalized_bundle
    ).split("\n")
    _append_decision_workflow_sections(lines, decision_workflow)
    return "\n".join(lines)


def format_policy_lookup_answer_standard(
    items: list[dict[str, Any]],
    *,
    max_items: int = 6,
    normalized_bundle: dict[str, Any] | None = None,
    answer_title: str | None = None,
) -> str:
    """Legacy single-shape policy answer (no decision/workflow appendix here)."""
    title = answer_title or "Internal policy manual — reference only (not legal advice; confirm with policy owners)."
    lines: list[str] = [
        title,
        "",
    ]
    norm = normalized_bundle or {}
    by_seg: dict[str, list[dict[str, Any]]] = norm.get("units_by_segment_id") or {}
    if norm.get("enabled") and by_seg:
        lines.append(
            "Structured fields below are heuristic labels from normalized knowledge units; "
            "they do not replace the segment excerpts."
        )
        lines.append("")

    if not items:
        lines.append(
            "No matching policy sections were found for this query. "
            "Try a shorter keyword or confirm policy ingest completed."
        )
        return "\n".join(lines)

    for i, it in enumerate(items[:max_items], start=1):
        head = it.get("heading") or f"Section {it.get('ordinal', '')}"
        lines.append(f"{i}. {head}")
        if it.get("anchor_key"):
            lines.append(f"   Anchor: {it.get('anchor_key')}")
        snip = (it.get("snippet") or "").strip()
        if snip:
            lines.append(f"   Excerpt: {snip[:2000]}")

        sid = str(it.get("ingestion_segment_id") or "")
        if sid and sid in by_seg:
            for j, nu in enumerate(by_seg[sid][:2], start=1):
                lines.append(f"   Normalized ({j}):")
                _append_normalized_lines(lines, nu, prefix="")
        lines.append("")

    lines.append("Confirm critical obligations with your policy administrator.")
    return "\n".join(lines)


def format_policy_lookup_answer(
    items: list[dict[str, Any]],
    *,
    max_items: int = 6,
    normalized_bundle: dict[str, Any] | None = None,
    decision_workflow: dict[str, Any] | None = None,
    answer_title: str | None = None,
    message: str | None = None,
    truth_packet: dict[str, Any] | None = None,
) -> str:
    """Policy manual: segment excerpts first; smart patterns when ``message`` is provided."""
    if (message or "").strip():
        from app.services.answer_patterns.integration import render_policy_smart_answer

        return render_policy_smart_answer(
            message=message or "",
            items=items,
            normalized_bundle=normalized_bundle,
            decision_workflow=decision_workflow,
            max_items=max_items,
            truth_packet=truth_packet,
            answer_title=answer_title,
        )
    lines = format_policy_lookup_answer_standard(
        items, max_items=max_items, normalized_bundle=normalized_bundle, answer_title=answer_title
    ).split("\n")
    _append_decision_workflow_sections(lines, decision_workflow)
    return "\n".join(lines)
