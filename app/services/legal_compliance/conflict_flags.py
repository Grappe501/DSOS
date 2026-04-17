"""
Purpose:
    Detect overlapping or contradictory snippets across families or date layers (flag only).

Role in Malone:
    Surfaces “needs human review” when retrieval returns conflicting passages.

Expected inputs:
    Candidate chunk set for a query.

Expected outputs:
    Boolean flags + reasons stored in trace `meta_json`.

TODO boundary:
    No automated resolution of true legal conflicts.
"""

from __future__ import annotations
