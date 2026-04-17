#!/usr/bin/env python3
"""
Scan tracking/data/internal_company_knowledge/, classify, register, and ingest via the control plane.

Examples:

  python tools/run_internal_company_ingest.py --dry-run

  python tools/run_internal_company_ingest.py --ingest --promotion none

  python tools/run_internal_company_ingest.py --intake-root tracking/data/internal_company_knowledge \\
    --emit-manifest tracking/ingestion_packs/internal_company_knowledge/internal_company_knowledge_manifest.json \\
    --emit-report tracking/reports/internal_company_ingest_last_run.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.db.session import SessionLocal  # noqa: E402
from app.services.internal_company_ingest.orchestration import run_internal_company_batch  # noqa: E402


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    default_intake = os.path.join(_REPO_ROOT, "tracking", "data", "internal_company_knowledge")
    default_manifest = os.path.join(
        _REPO_ROOT, "tracking", "ingestion_packs", "internal_company_knowledge", "internal_company_knowledge_manifest.json"
    )
    default_report = os.path.join(_REPO_ROOT, "tracking", "reports", "internal_company_ingest_last_run.json")

    p = argparse.ArgumentParser(description="Internal company knowledge intake (control-plane only).")
    p.add_argument("--intake-root", default=default_intake, help="Root folder to scan")
    p.add_argument("--dry-run", action="store_true", help="Classify and manifest only (default if --ingest not set)")
    p.add_argument("--ingest", action="store_true", help="Run real ingestion jobs")
    p.add_argument(
        "--promotion",
        choices=["none", "if_pass", "if_pass_or_warn"],
        default="none",
        help="Promotion mode forwarded to run_business_ingest (conservative default: none)",
    )
    p.add_argument("--version-label", default="v1")
    p.add_argument("--no-normalize", action="store_true", help="Skip post-ingest normalization for policy/SOP paths")
    p.add_argument("--emit-manifest", default=default_manifest, help="Write aggregate manifest JSON")
    p.add_argument("--emit-report", default=default_report, help="Write run report JSON")
    args = p.parse_args()

    dry = not args.ingest
    db = SessionLocal()
    try:
        out = run_internal_company_batch(
            db,
            intake_root=args.intake_root,
            dry_run=dry,
            promotion_mode=args.promotion,
            version_label=args.version_label,
            emit_manifest_path=args.emit_manifest,
            emit_report_path=args.emit_report,
            run_normalization_after_ingest=not args.no_normalize,
        )
        payload = {"run_timestamp": _utc_iso(), "args": vars(args), "result": out}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        st = out.get("batch_validation_status") or ""
        if st == "FAIL":
            return 2
        if st == "PASS_WITH_WARNINGS":
            return 1
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
