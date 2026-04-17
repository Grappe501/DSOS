"""
Inspect decision/workflow reasoning output from synthetic bundles (no server).

Example:
  python tools/debug_decision_reasoning.py
"""

from __future__ import annotations

import json
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.services.decision_reasoning import build_decision_workflow_block


def main() -> None:
    legal = {
        "enabled": True,
        "normalized": {
            "enabled": True,
            "units_by_chunk_id": {
                "c1": [
                    {
                        "id": "nu-legal-1",
                        "normalized_unit_type": "requirement",
                        "source_type": "legal_handbook",
                        "plain_language_summary": "Maintain required logs.",
                        "condition_text": "When dispensing.",
                        "exception_text": "",
                        "escalation_text": "Report to board if breach.",
                        "review_state": "approved",
                        "confidence_level": "high",
                        "legal_unit_chunk_id": "c1",
                    }
                ]
            },
        },
    }
    block = build_decision_workflow_block(
        message="What should we do and when do we escalate?",
        legal_bundle=legal,
        policy_bundle=None,
        sop_bundle=None,
        enabled=True,
    )
    print(json.dumps(block, indent=2, default=str))


if __name__ == "__main__":
    main()
