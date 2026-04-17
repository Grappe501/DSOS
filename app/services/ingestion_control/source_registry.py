"""CRUD helpers for ``ingestion_sources`` and ``ingestion_source_versions``."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionSource, IngestionSourceVersion
from app.models.models import gen_id


def get_or_create_source(
    db: Session,
    *,
    stable_key: str,
    source_type: str,
    title: str,
    business_domain: str = "general",
    owner_steward: str | None = None,
    authority_tier: str = "internal",
    lifecycle_status: str = "registered",
    meta: dict[str, Any] | None = None,
) -> tuple[IngestionSource, bool]:
    row = db.query(IngestionSource).filter(IngestionSource.stable_key == stable_key).one_or_none()
    if row:
        return row, False
    row = IngestionSource(
        id=gen_id(),
        stable_key=stable_key,
        source_type=source_type,
        business_domain=business_domain,
        owner_steward=owner_steward,
        authority_tier=authority_tier,
        lifecycle_status=lifecycle_status,
        title=title,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.add(row)
    db.flush()
    return row, True


def create_source_version(
    db: Session,
    *,
    ingestion_source_id: str,
    version_label: str,
    parser_profile_key: str,
    content_checksum: str | None = None,
    storage_uri: str | None = None,
    legal_document_id: str | None = None,
    legal_source_version_id: str | None = None,
    status: str = "draft",
    retrieval_ready: bool = False,
    meta: dict[str, Any] | None = None,
) -> IngestionSourceVersion:
    row = IngestionSourceVersion(
        id=gen_id(),
        ingestion_source_id=ingestion_source_id,
        version_label=version_label,
        content_checksum=content_checksum,
        storage_uri=storage_uri,
        parser_profile_key=parser_profile_key,
        legal_document_id=legal_document_id,
        legal_source_version_id=legal_source_version_id,
        status=status,
        retrieval_ready=retrieval_ready,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.add(row)
    db.flush()
    return row
