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


def format_legal_lookup_answer(
    items: list[dict[str, Any]],
    *,
    max_items: int = 6,
    normalized_bundle: dict[str, Any] | None = None,
) -> str:
    """
    Citation-first, inspectable text. Not a substitute for official sources.

    When ``normalized_bundle`` contains ``units_by_chunk_id``, structured fields are appended
    **after** citation lines for the same chunk (additive augmentation).
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


def format_policy_lookup_answer(
    items: list[dict[str, Any]],
    *,
    max_items: int = 6,
    normalized_bundle: dict[str, Any] | None = None,
) -> str:
    """Policy manual: segment excerpts first, optional normalized augmentation."""
    lines: list[str] = [
        "Internal policy manual — reference only (not legal advice; confirm with policy owners).",
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
