"""
Purpose:
    Legal-domain guardrails: authority typing, conflict flags, effective-date signals,
    escalation when corpus is ambiguous or out of scope.

Role in Malone:
    Advises `legal_assistant` and trace logging; does not replace human compliance review.

Expected inputs:
    Chunk metadata, date layers, actor context.

Expected outputs:
    Flags and human-readable reasons suitable for `meta_json` on traces.

TODO boundary:
    Not a substitute for counsel; surfaces uncertainty and source boundaries only.
"""

from __future__ import annotations
