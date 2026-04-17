"""
Enrich citation `anchor_json` with display-oriented strings for Malone-facing outputs.

Purpose:
    Stable human-facing labels (family line, statute line, page span) derived from structured fields.

Role in Malone:
    Future render/verification can quote these without inventing legal citations.
"""

from __future__ import annotations

import re
from typing import Any

_STATUTE = re.compile(r"^\d{1,3}-\d{1,3}-\d{1,4}$")


def enrich_anchor_display(
    base: dict[str, Any],
    *,
    compilation_label: str | None = None,
) -> dict[str, Any]:
    """Return a new dict with `display` and optional `compilation_label` keys."""
    out = dict(base)
    if compilation_label is not None:
        out["compilation_label"] = compilation_label

    cite = out.get("legal_citation")
    display: dict[str, Any] = {}
    if isinstance(cite, str) and _STATUTE.match(cite.strip()):
        display["statute"] = f"Ark. Code Sec. {cite.strip()}"
    fam_code = out.get("family_code")
    fam_title = out.get("family_title")
    if fam_code or fam_title:
        display["family"] = f"Family {fam_code or '?'}" + (
            f" / {fam_title}" if fam_title else ""
        )

    ps, pe = out.get("page_start"), out.get("page_end")
    if isinstance(ps, int) and isinstance(pe, int):
        display["pages"] = f"{ps}–{pe}" if ps != pe else str(ps)
    elif isinstance(ps, int):
        display["pages"] = str(ps)

    sub = out.get("subsection_path")
    if isinstance(sub, str) and sub.strip():
        display["subsection"] = sub.strip()

    if display:
        out["display"] = display
    return out
