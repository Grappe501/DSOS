"""Promotion / activation for ingestion source versions (governance, not Malone answer loop)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionPromotion, IngestionSource, IngestionSourceVersion
from app.models.models import gen_id


def promote_source_version(
    db: Session,
    *,
    ingestion_source_version_id: str,
    to_status: str = "promoted_active",
    actor: str | None = None,
    reason: str | None = None,
    meta: dict[str, Any] | None = None,
) -> tuple[IngestionPromotion, IngestionSourceVersion]:
    ver = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == ingestion_source_version_id).one()
    prev = ver.status
    ver.status = to_status
    ver.retrieval_ready = True
    m = json.loads(ver.meta_json or "{}")
    if meta:
        m.update(meta)
    m["promoted"] = True
    ver.meta_json = json.dumps(m, ensure_ascii=False)

    src = db.query(IngestionSource).filter(IngestionSource.id == ver.ingestion_source_id).one()
    if to_status == "promoted_active":
        src.lifecycle_status = "active"

    prom = IngestionPromotion(
        id=gen_id(),
        ingestion_source_version_id=ver.id,
        from_status=prev,
        to_status=to_status,
        promotion_outcome="applied",
        actor=actor,
        reason=reason,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.add(prom)
    db.flush()
    return prom, ver


def archive_source_version(
    db: Session,
    *,
    ingestion_source_version_id: str,
    actor: str | None = None,
    reason: str | None = None,
) -> tuple[IngestionPromotion, IngestionSourceVersion]:
    ver = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == ingestion_source_version_id).one()
    prev = ver.status
    ver.status = "archived"
    ver.retrieval_ready = False
    prom = IngestionPromotion(
        id=gen_id(),
        ingestion_source_version_id=ver.id,
        from_status=prev,
        to_status="archived",
        promotion_outcome="applied",
        actor=actor,
        reason=reason,
        meta_json="{}",
    )
    db.add(prom)
    db.flush()
    return prom, ver
