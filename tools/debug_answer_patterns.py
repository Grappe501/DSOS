"""
Print deterministic pattern selection for sample messages (no DB).

  python tools/debug_answer_patterns.py
"""

from __future__ import annotations

import json
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.services.answer_patterns.pattern_selector import select_answer_pattern


def main() -> None:
    samples = [
        ("legal_handbook", "What is required for PDMP — is this mandatory?"),
        ("legal_handbook", "Where does it say that — show me the citation?"),
        ("policy_manual", "Walk me through the process step by step."),
        ("policy_manual", "Are there exceptions — what if we are closed?"),
    ]
    for st, msg in samples:
        sel = select_answer_pattern(message=msg, source_type=st, normalized_units=[])
        print(json.dumps({"source_type": st, "message": msg, "selection": sel}, indent=2))


if __name__ == "__main__":
    main()
