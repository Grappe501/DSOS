"""
Purpose:
    Classify and validate `authority_type` on units/chunks (statute, administrative rule, etc.).

Role in Malone:
    Drives filters and answer disclaimers (“board rule” vs “Ark. Code”).

Expected inputs:
    Parsed headings, citation_kind, family metadata.

Expected outputs:
    authority_type labels and confidence notes (deterministic rules).

TODO boundary:
    Edge cases defer to `conflict_flags` rather than guessing.
"""

from __future__ import annotations
