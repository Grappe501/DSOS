"""
Print a JSON operating-copilot block for a sample message (no DB).

Usage:
  python tools/debug_operating_copilot.py
  python tools/debug_operating_copilot.py --message "what should we do next"
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Ensure repo root on path when run as script
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.services.decision_reasoning import build_decision_workflow_block  # noqa: E402
from app.services.operating_copilot import build_operating_copilot_block  # noqa: E402


def _sample_bundles() -> tuple[dict, dict | None, dict | None]:
    legal_bundle = {
        "enabled": True,
        "items": [{"legal_unit_chunk_id": "c1", "citation_key": "K1"}],
        "normalized": {
            "enabled": True,
            "units_by_chunk_id": {
                "c1": [
                    {
                        "id": "u1",
                        "normalized_unit_type": "requirement",
                        "source_type": "legal_handbook",
                        "plain_language_summary": "Sample obligation.",
                        "review_state": "system_generated",
                        "confidence_level": "medium",
                        "legal_unit_chunk_id": "c1",
                    }
                ]
            },
        },
    }
    policy_bundle = {
        "enabled": True,
        "items": [{"ingestion_segment_id": "s1"}],
        "normalized": {
            "enabled": True,
            "units_by_segment_id": {
                "s1": [
                    {
                        "id": "u2",
                        "normalized_unit_type": "workflow_step",
                        "source_type": "policy_manual",
                        "plain_language_summary": "Sample internal step.",
                        "review_state": "system_generated",
                        "confidence_level": "medium",
                        "ingestion_segment_id": "s1",
                    }
                ]
            },
        },
    }
    return legal_bundle, policy_bundle, None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--message", default="What should we do next operationally?")
    p.add_argument("--no-enable-env", action="store_true", help="Do not force copilot + decision env flags.")
    args = p.parse_args()
    if not args.no_enable_env:
        os.environ.setdefault("MALONE_DECISION_REASONING_ENABLED", "1")
        os.environ.setdefault("MALONE_OPERATING_COPILOT_ENABLED", "1")

    lb, pb, sb = _sample_bundles()
    dw = build_decision_workflow_block(
        message=args.message,
        legal_bundle=lb,
        policy_bundle=pb,
        sop_bundle=sb,
        enabled=True,
    )
    block = build_operating_copilot_block(
        message=args.message,
        legal_bundle=lb,
        policy_bundle=pb,
        sop_bundle=sb,
        decision_workflow=dw,
        enabled=True,
    )
    print(json.dumps(block, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
