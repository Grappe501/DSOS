"""Print a sample malone_telemetry dict (offline; for manual inspection)."""

from __future__ import annotations

import json
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.services.telemetry.malone_turn_telemetry import build_turn_telemetry  # noqa: E402


def main() -> None:
    sample = build_turn_telemetry(
        truth_packet={
            "packet_meta": {"answer_pattern_selected": "workflow"},
            "answer_pattern": {"pattern_id": "workflow"},
            "operating_copilot": {
                "enabled": True,
                "primary_scenario": "next_steps",
                "fallback_reason": None,
                "emit_minimal_only": False,
                "scenario_route": {"primary_scenario": "next_steps"},
                "route_reasons": [],
                "evidence_scope": {"cross_source": True, "source_types_with_items": ["legal_handbook", "policy_manual"]},
                "context": {"source_types_present": ["legal_handbook", "policy_manual"]},
            },
            "decision_workflow": {"enabled": True, "sources_present": ["legal_handbook"]},
        },
        verification={"delivery_mode": "legal_grounded_deterministic", "verified": True},
        intent={"target": "legal_handbook", "mode": "answer"},
        proposal_id="sample-proposal",
        cross_source_legal_policy_triggered=False,
    )
    print(json.dumps(sample, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
