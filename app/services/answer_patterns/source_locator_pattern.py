"""Citation / location-first answer shape."""

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

    lines: list[str] = [
        "Arkansas State Board of Pharmacy handbook — internal reference (not legal advice)",
        "",
        "Answer pattern: Source locator (citation-first; not legal advice).",
        "",
        "Where this appears in the ingested compilation:",
        "",
    ]

    if not items:
        lines.append(
            "No matching excerpts were found in the ingested compilation for this query. "
            "Try a statute-style citation, a shorter phrase, or confirm ingest completed."
        )
        return "\n".join(lines)

    for i, it in enumerate(items[:max_items], start=1):
        cite = it.get("citation_key") or it.get("primary_citation") or "—"
        fam = it.get("family_title") or it.get("family_code") or ""
        head = it.get("heading_raw")
        path = it.get("subsection_path")
        lines.append(f"{i}. Primary citation: {cite}")
        if fam:
            lines.append(f"   Family: {fam}")
        if head:
            lines.append(f"   Title / heading: {head}")
        if path:
            lines.append(f"   Subsection path: {path}")
        lines.append(f"   Pages: {sf.fmt_pages(it)}")
        snip = (it.get("snippet") or "").strip()
        rel = sf.first_sentence(snip, max_len=280) if snip else ""
        if rel:
            lines.append(f"   Relevance (excerpt lead-in): {rel}")
        lines.append("   Full excerpt:")
        if snip:
            lines.append(f"   {snip}")
        cid = str(it.get("legal_unit_chunk_id") or "")
        if cid and cid in by_chunk:
            for j, nu in enumerate(by_chunk[cid][:2], start=1):
                lines.append(f"   Normalized ({j}):")
                sf.append_normalized_lines(lines, nu, prefix="")
        lines.append("")

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

    lines: list[str] = [title, "", "Answer pattern: Source locator (section-first).", "", "Where this appears:", ""]

    if not items:
        lines.append("No matching policy sections were found for this query.")
        return "\n".join(lines)

    for i, it in enumerate(items[:max_items], start=1):
        head = it.get("heading") or f"Section {it.get('ordinal', '')}"
        lines.append(f"{i}. Section: {head}")
        if it.get("anchor_key"):
            lines.append(f"   Anchor: {it.get('anchor_key')}")
        snip = (it.get("snippet") or "").strip()
        rel = sf.first_sentence(snip, max_len=280) if snip else ""
        if rel:
            lines.append(f"   Relevance (excerpt lead-in): {rel}")
        lines.append("   Full excerpt:")
        if snip:
            lines.append(f"   {snip[:2000]}")
        sid = str(it.get("ingestion_segment_id") or "")
        if sid and sid in by_seg:
            for j, nu in enumerate(by_seg[sid][:2], start=1):
                lines.append(f"   Normalized ({j}):")
                sf.append_normalized_lines(lines, nu, prefix="")
        lines.append("")

    lines.append("Confirm critical obligations with your policy administrator.")
    return "\n".join(lines)
