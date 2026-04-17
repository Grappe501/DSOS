"""policy_manual → normalized units from ingestion_segments (deterministic)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.services.knowledge_normalization.confidence import confidence_for_keyword_rules
from app.services.knowledge_normalization.field_extractors import extract_signals, first_sentence
from app.services.knowledge_normalization import unit_types as UT


@dataclass(frozen=True)
class PolicyDraftUnit:
    ordinal: int
    normalized_unit_type: str
    title: str | None
    source_text: str
    plain_language_summary: str | None
    applies_to_role: str | None
    action_type: str | None
    requirement_level: str | None
    citation_keys_json: str
    anchor_json: str
    structured_facets_json: str
    confidence_level: str
    ingestion_segment_id: str
    ingestion_source_id: str
    ingestion_source_version_id: str
    retrieval_headline: str | None
    retrieval_blob: str | None
    meta_json: str


def _classify_policy(sig: Any, text: str) -> tuple[str, str | None]:
    if sig.is_definition_like:
        return UT.UNIT_DEFINITION, None
    if sig.is_prohibition:
        return UT.UNIT_POLICY_RULE, UT.ACTION_PROHIBITION
    if sig.is_escalation:
        return UT.UNIT_ESCALATION_RULE, UT.ACTION_OBLIGATION
    if sig.requirement_level in ("must", "should"):
        return UT.UNIT_POLICY_RULE, UT.ACTION_OBLIGATION
    return UT.UNIT_POLICY_RULE, UT.ACTION_UNKNOWN


def build_policy_units(
    db: Session,
    *,
    ingestion_source_id: str,
    ingestion_source_version_id: str,
    source_type: str = "policy_manual",
) -> list[PolicyDraftUnit]:
    from app.models.ingestion_control import IngestionSegment

    segs = (
        db.query(IngestionSegment)
        .filter(IngestionSegment.ingestion_source_version_id == ingestion_source_version_id)
        .order_by(IngestionSegment.ordinal)
        .all()
    )
    out: list[PolicyDraftUnit] = []
    for seg in segs:
        text = (seg.body_text or "").strip()
        if not text:
            continue
        title = seg.heading
        sig = extract_signals(text, title)
        utype, action = _classify_policy(sig, text)
        conf = confidence_for_keyword_rules(
            matched_rules=sig.matched_rule_count, text_len=len(text)
        )
        anchor = {
            "ingestion_segment_id": seg.id,
            "anchor_key": seg.anchor_key,
            "ordinal": seg.ordinal,
        }
        try:
            meta = json.loads(seg.meta_json or "{}")
        except json.JSONDecodeError:
            meta = {}
        if not isinstance(meta, dict):
            meta = {}
        role = None
        if isinstance(meta, dict):
            role = meta.get("applies_to_role") or meta.get("role")

        facets = {
            "extraction": "policy_keyword_rules_v1",
            "segment_ordinal": seg.ordinal,
        }
        headline = (title or "")[:200] or f"segment-{seg.ordinal}"
        retrieval_blob = " ".join(x for x in [title or "", first_sentence(text)] if x)

        out.append(
            PolicyDraftUnit(
                ordinal=len(out),
                normalized_unit_type=utype,
                title=title,
                source_text=text,
                plain_language_summary=first_sentence(text) or None,
                applies_to_role=role,
                action_type=action,
                requirement_level=sig.requirement_level if sig.requirement_level != "unknown" else None,
                citation_keys_json="[]",
                anchor_json=json.dumps(anchor, ensure_ascii=False, sort_keys=True),
                structured_facets_json=json.dumps(facets, ensure_ascii=False, sort_keys=True),
                confidence_level=conf,
                ingestion_segment_id=seg.id,
                ingestion_source_id=ingestion_source_id,
                ingestion_source_version_id=ingestion_source_version_id,
                retrieval_headline=headline[:500],
                retrieval_blob=retrieval_blob[:8000],
                meta_json=json.dumps({"profile": "policy_manual_v1"}, ensure_ascii=False),
            )
        )
    return out
