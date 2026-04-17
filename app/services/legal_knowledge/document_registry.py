"""
Persistence helpers for `legal_documents` and `legal_source_versions`.

Role in Malone:
    Ingestion jobs register stable document identity before chunks exist.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_handbook import LegalDocument, LegalSourceVersion


def create_legal_document(
    db: Session,
    *,
    stable_key: str,
    title: str,
    compiled_edition_label: str | None = None,
    original_filename: str | None = None,
    storage_uri: str | None = None,
    content_checksum: str | None = None,
    cover_metadata: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> LegalDocument:
    row = LegalDocument(
        stable_key=stable_key,
        title=title,
        compiled_edition_label=compiled_edition_label,
        original_filename=original_filename,
        storage_uri=storage_uri,
        content_checksum=content_checksum,
        cover_metadata_json=json.dumps(cover_metadata or {}, ensure_ascii=False),
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
        status="registered",
    )
    db.add(row)
    db.flush()
    return row


def create_legal_source_version(
    db: Session,
    *,
    legal_document_id: str,
    version_label: str,
    compiled_publication_date: str | None = None,
    content_checksum: str | None = None,
    storage_uri: str | None = None,
    status: str = "active",
    meta: dict[str, Any] | None = None,
) -> LegalSourceVersion:
    row = LegalSourceVersion(
        legal_document_id=legal_document_id,
        version_label=version_label,
        compiled_publication_date=compiled_publication_date,
        content_checksum=content_checksum,
        storage_uri=storage_uri,
        status=status,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.add(row)
    db.flush()
    return row
