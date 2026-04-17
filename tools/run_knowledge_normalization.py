"""
CLI: run knowledge normalization for a legal or policy source version.

Examples (repo root):

  python tools/run_knowledge_normalization.py --legal-source-version-id <uuid>

  python tools/run_knowledge_normalization.py \\
    --ingestion-source-version-id <uuid> --ingestion-source-id <uuid> --source-type policy_manual
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main(argv: list[str] | None = None) -> int:
    from sqlalchemy.orm import Session

    import app.models.ingestion_control  # noqa: F401
    import app.models.knowledge_normalization  # noqa: F401
    import app.models.legal_handbook  # noqa: F401
    import app.models.models  # noqa: F401

    from app.db.session import SessionLocal
    from app.services.knowledge_normalization.normalization_runner import run_normalization

    p = argparse.ArgumentParser(description="Knowledge normalization runner")
    p.add_argument("--legal-source-version-id", default=None, help="LegalSourceVersion.id")
    p.add_argument("--ingestion-source-version-id", default=None, help="IngestionSourceVersion.id")
    p.add_argument("--ingestion-source-id", default=None, help="IngestionSource.id (policy path)")
    p.add_argument(
        "--legal-document-id",
        default=None,
        help="Optional LegalDocument.id override when normalizing legal handbook",
    )
    p.add_argument(
        "--source-type",
        default="legal_handbook",
        help="legal_handbook | policy_manual (default: legal_handbook)",
    )
    p.add_argument("--profile", default=None, help="Override normalization profile key")
    p.add_argument(
        "--reports-dir",
        default=os.path.join(_REPO_ROOT, "tracking", "reports"),
        help="Directory for run JSON/Markdown",
    )
    args = p.parse_args(argv)

    db: Session = SessionLocal()
    try:
        out = run_normalization(
            db,
            source_type=args.source_type,
            profile_key=args.profile,
            legal_source_version_id=args.legal_source_version_id,
            ingestion_source_version_id=args.ingestion_source_version_id,
            ingestion_source_id=args.ingestion_source_id,
            legal_document_id=args.legal_document_id,
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()

    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    state_path = reports_dir / "knowledge_normalization_last_run.json"
    payload = {
        "run_timestamp": _utc_now_iso(),
        "result": out,
        "args": vars(args),
    }
    state_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(out, indent=2, ensure_ascii=False))
    status = out.get("validation_status") or "FAIL"
    if status == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
