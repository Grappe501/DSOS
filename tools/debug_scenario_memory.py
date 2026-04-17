"""
Inspect scenario memory + decision trace persistence (requires DB with tables).

Usage:
  python tools/debug_scenario_memory.py --list 5
  python tools/debug_scenario_memory.py --scenario-id <uuid>
"""

from __future__ import annotations

import argparse
import json
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--list", type=int, metavar="N", help="List N recent scenario memories")
    p.add_argument("--scenario-id", type=str, help="Print decision trace JSON for scenario id")
    args = p.parse_args()

    from app.db.session import SessionLocal
    from app.models.scenario_memory import MaloneDecisionTrace, MaloneScenarioMemory

    db = SessionLocal()
    try:
        if args.list:
            rows = (
                db.query(MaloneScenarioMemory).order_by(MaloneScenarioMemory.created_at.desc()).limit(args.list).all()
            )
            for r in rows:
                print(r.id, r.scenario_type, r.intent_target, str(r.created_at))
            return 0
        if args.scenario_id:
            tr = (
                db.query(MaloneDecisionTrace).filter(MaloneDecisionTrace.scenario_memory_id == args.scenario_id).first()
            )
            if not tr:
                print("No trace for scenario id", file=sys.stderr)
                return 1
            print(
                json.dumps(
                    {
                        "answer_pattern": json.loads(tr.answer_pattern_json or "{}"),
                        "decision_workflow_keys": list(json.loads(tr.decision_workflow_json or "{}").keys())[:30],
                    },
                    indent=2,
                )
            )
            return 0
        p.print_help()
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
