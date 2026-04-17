"""
Purpose:
    Canonicalize extracted text for deterministic chunking (unicode normalization,
    whitespace, line breaks).

Role in Malone:
    Stable normalization reduces spurious chunk boundaries that would break citations
    and retrieval.

Expected inputs:
    Raw string from the parser.

Expected outputs:
    A single normalized string passed to the chunker.

Notes:
    This is a foundation scaffold for the regulation engine.
    Implementation is intentionally deferred to the next build pass.
"""

from __future__ import annotations

import re
import unicodedata


_WS = re.compile(r"[ \t]+")
_LINES = re.compile(r"\n{3,}")


def normalize_extracted_text(raw: str) -> str:
    if not raw:
        return ""
    text = unicodedata.normalize("NFKC", raw)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _LINES.sub("\n\n", text)
    lines = [_WS.sub(" ", line).strip() for line in text.split("\n")]
    return "\n".join(lines).strip()
