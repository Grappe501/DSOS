"""Dimensional tagging for business sources and segments."""

from __future__ import annotations

import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.ingestion_control import IngestionTagAssignment, IngestionTagDefinition
from app.models.models import gen_id

# Dimensions required by the architecture pass (extensible).
DOMAIN = "domain"
TOPIC = "topic"
DOCUMENT_TYPE = "document_type"
ROLE = "role"
ACTION_TYPE = "action_type"
REVIEW_STATE = "review_state"

TAG_DIMENSIONS = frozenset(
    {
        DOMAIN,
        TOPIC,
        DOCUMENT_TYPE,
        ROLE,
        ACTION_TYPE,
        REVIEW_STATE,
    }
)


def _slug(s: str) -> str:
    x = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower()).strip("-")
    return x or "tag"


def ensure_tag_definition(
    db: Session,
    *,
    dimension: str,
    slug: str,
    label: str,
    meta: dict[str, Any] | None = None,
) -> IngestionTagDefinition:
    row = (
        db.query(IngestionTagDefinition)
        .filter(IngestionTagDefinition.dimension == dimension, IngestionTagDefinition.slug == slug)
        .one_or_none()
    )
    if row:
        return row
    row = IngestionTagDefinition(
        id=gen_id(),
        dimension=dimension,
        slug=slug,
        label=label,
        parent_id=None,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.add(row)
    db.flush()
    return row


def assign_tag(
    db: Session,
    *,
    tag_definition_id: str,
    target_kind: str,
    target_id: str,
) -> IngestionTagAssignment:
    existing = (
        db.query(IngestionTagAssignment)
        .filter(
            IngestionTagAssignment.tag_definition_id == tag_definition_id,
            IngestionTagAssignment.target_kind == target_kind,
            IngestionTagAssignment.target_id == target_id,
        )
        .one_or_none()
    )
    if existing:
        return existing
    row = IngestionTagAssignment(
        id=gen_id(),
        tag_definition_id=tag_definition_id,
        target_kind=target_kind,
        target_id=target_id,
    )
    db.add(row)
    db.flush()
    return row


def tag_source_version_from_map(
    db: Session,
    *,
    ingestion_source_version_id: str,
    tags: dict[str, str],
) -> list[IngestionTagAssignment]:
    """
    ``tags`` maps dimension -> human label (slug derived).

    Example: {"domain": "Pharmacy Operations", "role": "Pharmacist"}
    """
    out: list[IngestionTagAssignment] = []
    for dimension, label in tags.items():
        if dimension not in TAG_DIMENSIONS:
            continue
        slug = _slug(label)
        d = ensure_tag_definition(db, dimension=dimension, slug=slug, label=label)
        out.append(
            assign_tag(
                db,
                tag_definition_id=d.id,
                target_kind="source_version",
                target_id=ingestion_source_version_id,
            )
        )
    return out
