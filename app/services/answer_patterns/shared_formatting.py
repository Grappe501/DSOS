"""Shared line builders for legal/policy deterministic answers (no LLM)."""

from __future__ import annotations

from typing import Any


def fmt_pages(item: dict[str, Any]) -> str:
    ps = item.get("page_start")
    pe = item.get("page_end")
    if ps is None and pe is None:
        return "unknown"
    if pe is None or pe == ps:
        return str(ps)
    return f"{ps}–{pe}"


def append_normalized_lines(lines: list[str], nu: dict[str, Any], prefix: str) -> None:
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


def first_sentence(text: str, *, max_len: int = 240) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    for sep in ".?\n":
        if sep in t[:400]:
            t = t.split(sep)[0] + (sep if sep != "\n" else "")
            break
    return t[:max_len].strip()


def collect_roles(units: list[dict[str, Any]]) -> list[str]:
    roles: set[str] = set()
    for u in units:
        r = (u.get("applies_to_role") or "").strip()
        if r:
            roles.add(r)
    return sorted(roles)


def collect_requirement_levels(units: list[dict[str, Any]]) -> list[str]:
    out: set[str] = set()
    for u in units:
        rl = (u.get("requirement_level") or "").strip()
        if rl:
            out.add(rl)
    return sorted(out)


def bottom_line_from_units_or_items(units: list[dict[str, Any]], items: list[dict[str, Any]]) -> str:
    for u in units:
        s = (u.get("plain_language_summary") or "").strip()
        if s:
            return s[:900]
    for it in items:
        s = (it.get("snippet") or "").strip()
        if s:
            return first_sentence(s, max_len=500)
    return "See source excerpts below (no concise summary available from normalized fields)."


def default_rule_text(units: list[dict[str, Any]], items: list[dict[str, Any]]) -> str:
    for u in units:
        t = (u.get("normalized_unit_type") or "").lower()
        if t in ("requirement", "prohibition", "permission") and (u.get("plain_language_summary") or "").strip():
            return str(u.get("plain_language_summary"))[:900]
    for it in items:
        s = (it.get("snippet") or "").strip()
        if s:
            return first_sentence(s, max_len=700)
    return ""


def collect_exception_texts(units: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for u in units:
        e = (u.get("exception_text") or "").strip()
        if e and e not in seen:
            seen.add(e)
            out.append(e[:1200])
    return out


def collect_condition_texts(units: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for u in units:
        e = (u.get("condition_text") or "").strip()
        if e and e not in seen:
            seen.add(e)
            out.append(e[:1200])
    return out


def collect_reporting_texts(units: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for u in units:
        for key in ("output_outcome_text", "escalation_text"):
            e = (u.get(key) or "").strip()
            if e and e not in seen:
                seen.add(e)
                out.append(f"[{key}] {e[:800]}")
    return out


def build_legal_items_section(
    items: list[dict[str, Any]],
    *,
    by_chunk: dict[str, list[dict[str, Any]]],
    max_items: int,
) -> list[str]:
    lines: list[str] = []
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
        lines.append(f"   Pages: {fmt_pages(it)}")
        snip = (it.get("snippet") or "").strip()
        if snip:
            lines.append(f"   Excerpt: {snip}")
        cid = str(it.get("legal_unit_chunk_id") or "")
        if cid and cid in by_chunk:
            for j, nu in enumerate(by_chunk[cid][:2], start=1):
                lines.append(f"   Normalized ({j}):")
                append_normalized_lines(lines, nu, prefix="")
        lines.append("")
    return lines


def build_policy_items_section(
    items: list[dict[str, Any]],
    *,
    by_seg: dict[str, list[dict[str, Any]]],
    max_items: int,
) -> list[str]:
    lines: list[str] = []
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
                append_normalized_lines(lines, nu, prefix="")
        lines.append("")
    return lines
