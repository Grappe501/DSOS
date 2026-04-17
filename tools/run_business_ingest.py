#!/usr/bin/env python3
"""
CLI for business-wide ingestion control plane (registry + job + validation + optional promotion).

Examples:

  python tools/run_business_ingest.py --profile policy_manual --source-type policy_manual \\
    --path path/to/manual.md --stable-key POLICY_HR_001 --title "HR Policy Manual"

  python tools/run_business_ingest.py --profile legal_handbook --source-type legal_handbook \\
    --path path/to/lawbook.pdf --stable-key ARK_ASBP_STATUTES_RULES_2025_11 \\
    --title "Arkansas Statutes and Rules"
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
from app.services.ingestion_control.ingest_runner import run_business_ingest  # noqa: E402


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    p = argparse.ArgumentParser(description="Run a business ingestion job through the control plane.")
    p.add_argument("--stable-key", required=True, help="Stable identity for ingestion_sources.stable_key")
    p.add_argument("--title", required=True, help="Human title for the logical source")
    p.add_argument("--source-type", required=True, help="e.g. legal_handbook, policy_manual, sop_workflow")
    p.add_argument("--profile", required=True, help="Parser profile key (see parser_profiles.PARSER_PROFILES)")
    p.add_argument("--path", required=True, help="File path (PDF for legal_handbook, text/markdown otherwise)")
    p.add_argument("--version-label", default="v1", help="Version label for this ingest")
    p.add_argument("--domain", default="general", help="business_domain on ingestion_sources")
    p.add_argument("--owner", default=None, help="owner_steward string (email or role id)")
    p.add_argument("--authority-tier", default="internal", help="authority_tier on ingestion_sources")
    p.add_argument("--no-validate", action="store_true", help="Skip validation persistence")
    p.add_argument(
        "--promotion",
        choices=["none", "if_pass", "if_pass_or_warn"],
        default="none",
        help="Auto-promote ingestion_source_version when validation matches",
    )
    p.add_argument(
        "--tags-json",
        default=None,
        help='Optional JSON object of dimensional tags, e.g. {"domain":"Pharmacy","role":"PIC"}',
    )
    p.add_argument(
        "--emit-report",
        default=os.path.join(_REPO_ROOT, "tracking", "reports", "business_ingest_last_run.json"),
        help="Write machine-readable run summary JSON",
    )
    args = p.parse_args()

    tags: dict[str, str] | None = None
    if args.tags_json:
        tags = json.loads(args.tags_json)
        if not isinstance(tags, dict):
            raise SystemExit("--tags-json must be a JSON object")

    db = SessionLocal()
    try:
        out = run_business_ingest(
            db,
            stable_key=args.stable_key,
            source_type=args.source_type,
            parser_profile_key=args.profile,
            source_path=args.path,
            title=args.title,
            business_domain=args.domain,
            owner_steward=args.owner,
            authority_tier=args.authority_tier,
            version_label=args.version_label,
            run_validation=not args.no_validate,
            promotion_mode=args.promotion,
            dimensional_tags=tags,
        )
        payload = {"run_timestamp": _utc_iso(), "args": vars(args), "result": out}
        os.makedirs(os.path.dirname(args.emit_report) or ".", exist_ok=True)
        with open(args.emit_report, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        failed = out.get("status") == "failed" or out.get("validation_status") == "FAIL"
        return 0 if not failed else 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
