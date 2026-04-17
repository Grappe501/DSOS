#!/usr/bin/env python3
"""Print workflow extraction JSON for stdin text or --sample."""

from __future__ import annotations

import argparse
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from app.services.workflow_extraction import extract_workflow_fields_from_text  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--text", default=None, help="Raw text to extract from")
    p.add_argument("--sample", action="store_true", help="Run built-in SOP-like sample")
    args = p.parse_args()
    if args.sample:
        text = (
            "Prerequisites: Two witnesses.\n\n"
            "1. Verify prescription.\n2. Check storage.\n"
            "Stop if temperature out of range.\n"
            "Escalate to the pharmacist if unclear.\n"
            "If the order is denied, notify compliance."
        )
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    out = extract_workflow_fields_from_text(text)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
