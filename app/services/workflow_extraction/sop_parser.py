"""Split SOP-like text into lines for deterministic extraction."""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def split_lines(text: str) -> list[str]:
    if not text:
        return []
    return [ln.strip() for ln in text.replace("\r\n", "\n").split("\n") if ln.strip()]


def combined_unit_text(unit: dict[str, Any]) -> str:
    """Primary text surface for extraction (no fabrication)."""
    parts = [
        (unit.get("title") or "").strip(),
        (unit.get("plain_language_summary") or "").strip(),
    ]
    return normalize_whitespace("\n\n".join(p for p in parts if p))
