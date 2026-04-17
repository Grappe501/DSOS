"""
Purpose:
    Declarative ingestion profile for compiled pharmacy law handbooks (Arkansas ASBP-style).

Role in Malone:
    Central configuration for parsers: TOC family codes, citation patterns, subsection
    depth order, and date-layer hints—without embedding runtime logic.

Expected inputs:
    Deployment constants or environment-driven overrides (future).

Expected outputs:
    Immutable profile dict / dataclass instances consumed by `source_profiler` and parsers.

TODO boundary:
    Does not read files or touch the database; definitions only.
"""

from __future__ import annotations

# Arkansas compiled handbook: major families labeled A–H in TOC; embedded dates vary by act.
HANDBOOK_FAMILY_CODES: tuple[str, ...] = tuple(chr(ord("A") + i) for i in range(8))

# Statute-style citations (examples: 17-92-101, 5-64-101) — detection is implemented later.
STATUTE_CITATION_PATTERN_HINT = r"\b\d+-\d+-\d+\b"
