"""Build manifest entries and aggregate JSON for internal company intake."""

from __future__ import annotations

import json
from typing import Any

from app.services.internal_company_ingest.classification import ClassificationResult, stable_key_for
from app.services.internal_company_ingest.intake_discovery import DiscoveredFile, path_checksum_token


def manifest_entry_from_discovery(
    df: DiscoveredFile,
    cls: ClassificationResult,
) -> dict[str, Any]:
    tok = path_checksum_token(df.absolute_path)
    sk = stable_key_for(df.folder_segment or "root", df.filename, tok)
    title = df.filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").strip() or df.filename
    return {
        "proposed_stable_key": sk,
        "file_path": df.absolute_path.replace("\\", "/"),
        "relative_path": df.relative_path,
        "source_title": title[:500],
        "source_type": cls.source_type,
        "parser_profile": cls.parser_profile_key,
        "business_domain": cls.business_domain,
        "tags": {
            "internal_category": cls.internal_category,
            "classification_reason": cls.classification_reason,
        },
        "authority_hint": cls.authority_tier,
        "review_recommendation": cls.review_recommendation,
        "ingestion_priority": cls.ingestion_priority,
        "active_candidate": cls.active_candidate,
        "normalization_profile_hint": cls.normalization_profile,
        "notes": cls.notes,
    }


def write_json(path: str, payload: Any) -> None:
    import os

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
