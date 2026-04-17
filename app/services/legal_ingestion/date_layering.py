"""
Persist explicit date layers (compiled edition vs embedded act dates).

Role in Malone:
    `legal_date_layers` rows back compliance/effective-date reasoning without mixing layers.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_handbook import LegalDateLayer


def record_family_embedded_revision(
    db: Session,
    *,
    family_row_id: str,
    raw_label: str,
    meta: dict[str, Any] | None = None,
) -> LegalDateLayer:
    row = LegalDateLayer(
        scope_type="legal_document_family",
        scope_id=family_row_id,
        layer_kind="embedded_source_revision",
        raw_label=raw_label,
        iso_date=None,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.add(row)
    db.flush()
    return row


def record_compilation_edition_layer(
    db: Session,
    *,
    legal_source_version_id: str,
    raw_label: str,
    meta: dict[str, Any] | None = None,
) -> LegalDateLayer:
    row = LegalDateLayer(
        scope_type="legal_source_version",
        scope_id=legal_source_version_id,
        layer_kind="compiled_publication",
        raw_label=raw_label,
        iso_date=None,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.add(row)
    db.flush()
    return row
