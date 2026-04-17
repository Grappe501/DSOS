"""
Purpose:
    Filter chunks by `authority_type` (statute vs board rule vs federal reference) and
    deployment allowlists.

Role in Malone:
    Enforces “is this statute or rule?” and jurisdiction boundaries before answers.

Expected inputs:
    Candidate chunk ids, requested authority scope, actor role metadata.

Expected outputs:
    Filtered id list and exclusion reasons for audit.

TODO boundary:
    Policy tables may later align with `legal_compliance` escalation rules.
"""

from __future__ import annotations
