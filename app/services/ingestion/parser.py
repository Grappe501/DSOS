"""
Purpose:
    Extract machine-readable text (and optional structure) from handbook source files
    (PDF, HTML, text).

Role in Malone:
    Produces the raw material for chunking and storage; Malone never reads files
    directly—only chunks persisted after ingestion.

Expected inputs:
    File bytes, optional filename, source_type hint.

Expected outputs:
    ParserResult: text plus optional coarse blocks (e.g. pages, headings).

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.services.ingestion.normalizer import normalize_extracted_text


@dataclass
class ParserResult:
    text: str
    blocks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_handbook_bytes(
    data: bytes,
    *,
    filename: str | None = None,
    source_type: str = "handbook",
    profile: str | None = None,
) -> ParserResult:
    """
    Decode extracted bytes to text. PDF binary is not interpreted here — upstream OCR or
    `pdftotext` must supply UTF-8/text bytes for the Arkansas slice.

    When profile is `arkansas_asbp_compilation_text`, text is normalized for TOC + unit parsing.
    """
    del filename, source_type
    if not data:
        return ParserResult(text="", warnings=["empty_input"])
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
        warnings = ["decode_replaced_non_utf8"]
    else:
        warnings = []
    if profile == "arkansas_asbp_compilation_text":
        text = normalize_extracted_text(text)
    return ParserResult(text=text, warnings=warnings)
