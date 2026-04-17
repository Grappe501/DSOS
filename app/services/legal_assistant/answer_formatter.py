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


def format_legal_lookup_answer(items: list[dict[str, Any]], *, max_items: int = 6) -> str:
    """
    Citation-first, inspectable text. Not a substitute for official sources.
    """
    lines: list[str] = [
        "Arkansas State Board of Pharmacy handbook — internal reference (not legal advice)",
        "",
    ]
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
        lines.append("")

    lines.append(
        "Verify against your official compilation or primary legal resources. "
        "This tool summarizes ingested text only."
    )
    return "\n".join(lines)
