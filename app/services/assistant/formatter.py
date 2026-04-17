"""
Purpose:
    Turn evidence chunks into citation-first draft text suitable for structured render
    input (not free-form hallucination).

Role in Malone:
    Feeds the OpenAI render path only as part of an approved truth_packet / evidence
    envelope, subject to render_verifier.

Expected inputs:
    List of chunk dicts with citation_key and body or snippet fields.

Expected outputs:
    A single string with inline citation markers per project convention.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from typing import Any


def format_evidence_stub(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return ""
    lines = []
    for c in chunks:
        key = c.get("citation_key", "?")
        body = c.get("body_text") or c.get("snippet") or ""
        lines.append(f"[{key}] {body[:500]}")
    return "\n\n".join(lines)


def format_legal_handbook_evidence_stub(chunks: list[dict[str, Any]]) -> str:
    """Contract helper for legal retrieval hits (family + citation + subsection path)."""
    if not chunks:
        return ""
    lines: list[str] = []
    for c in chunks:
        fam = c.get("family_title") or c.get("family_code") or ""
        cite = c.get("citation_key") or c.get("primary_citation") or "?"
        sub = c.get("subsection_path") or ""
        body = c.get("body_text") or c.get("snippet") or ""
        prefix = f"{fam} | {cite}" + (f" | {sub}" if sub else "")
        lines.append(f"[{prefix}]\n{body[:800]}")
    return "\n\n".join(lines)
