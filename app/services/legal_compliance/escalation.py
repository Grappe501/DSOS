"""
Purpose:
    Escalation templates when retrieval is empty, ambiguous, or outside licensed corpus.

Role in Malone:
    Returns safe, deterministic user messaging paths aligned with clarification patterns.

Expected inputs:
    Retrieval diagnostics, compliance flags.

Expected outputs:
    Escalation recommendation (clarify, refuse, cite handbook limitation).

TODO boundary:
    Does not invoke workflows directly; callers map to `clarification_service` / audit.
"""

from __future__ import annotations
