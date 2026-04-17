"""
Debug: print normalized unit counts for a legal or policy source version.

  python tools/debug_normalized_retrieval.py --legal-source-version-id <uuid>
  python tools/debug_normalized_retrieval.py --ingestion-source-version-id <uuid>
"""

from __future__ import annotations

import argparse
import json
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def main() -> int:
    import app.models.knowledge_normalization  # noqa: F401
    import app.models.legal_handbook  # noqa: F401

    from sqlalchemy import func

    from app.db.session import SessionLocal
    from app.models.knowledge_normalization import NormalizedKnowledgeUnit

    p = argparse.ArgumentParser()
    p.add_argument("--legal-source-version-id", default=None)
    p.add_argument("--ingestion-source-version-id", default=None)
    args = p.parse_args()

    db = SessionLocal()
    try:
        q = db.query(func.count(NormalizedKnowledgeUnit.id))
        if args.legal_source_version_id:
            q = q.filter(NormalizedKnowledgeUnit.legal_source_version_id == args.legal_source_version_id)
        elif args.ingestion_source_version_id:
            q = q.filter(NormalizedKnowledgeUnit.ingestion_source_version_id == args.ingestion_source_version_id)
        else:
            print("Provide --legal-source-version-id or --ingestion-source-version-id", file=sys.stderr)
            return 1
        n = q.scalar() or 0
        print(json.dumps({"normalized_unit_count": int(n)}, indent=2))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
