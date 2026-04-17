"""legal_handbook → normalized knowledge units (chunk-grounded, deterministic)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.services.knowledge_normalization.confidence import confidence_for_keyword_rules
from app.services.knowledge_normalization.field_extractors import extract_signals, first_sentence
from app.services.knowledge_normalization.review_state import REVIEW_SYSTEM_GENERATED
from app.services.knowledge_normalization import unit_types as UT


@dataclass(frozen=True)
class DraftUnit:
    ordinal: int
    normalized_unit_type: str
    title: str | None
    source_text: str
    plain_language_summary: str | None
    applies_to_role: str | None
    action_type: str | None
    requirement_level: str | None
    condition_text: str | None
    exception_text: str | None
    escalation_text: str | None
    output_outcome_text: str | None
    citation_keys_json: str
    anchor_json: str
    structured_facets_json: str
    confidence_level: str
    legal_unit_id: str | None
    legal_unit_chunk_id: str
    legal_document_id: str | None
    legal_source_version_id: str
    retrieval_headline: str | None
    retrieval_blob: str | None
    meta_json: str


def _classify_unit(sig: Any, text: str) -> tuple[str, str | None, str | None]:
    """Returns (unit_type, action_type, requirement_level)."""
    if sig.is_definition_like:
        return UT.UNIT_DEFINITION, None, None
    if sig.is_prohibition:
        return UT.UNIT_PROHIBITION, UT.ACTION_PROHIBITION, sig.requirement_level if sig.requirement_level != "unknown" else UT.REQUIREMENT_LEVEL_MUST
    if sig.is_exception_like and not sig.is_definition_like:
        return UT.UNIT_EXCEPTION, None, sig.requirement_level
    if sig.is_escalation:
        return UT.UNIT_ESCALATION_RULE, UT.ACTION_OBLIGATION, sig.requirement_level
    if sig.is_reporting_duty:
        if "record" in text.lower() or "maintain" in text.lower():
            return UT.UNIT_DOCUMENTATION_RULE, UT.ACTION_OBLIGATION, sig.requirement_level
        return UT.UNIT_REPORTING_RULE, UT.ACTION_OBLIGATION, sig.requirement_level
    if sig.requirement_level == "must" or sig.requirement_level == "should":
        return UT.UNIT_REQUIREMENT, UT.ACTION_OBLIGATION, sig.requirement_level
    if sig.is_permission:
        return UT.UNIT_PERMISSION, UT.ACTION_PERMISSION, UT.REQUIREMENT_LEVEL_MAY
    return UT.UNIT_GENERAL, UT.ACTION_UNKNOWN, UT.REQUIREMENT_LEVEL_UNKNOWN


def build_legal_units(
    db: Session,
    *,
    legal_source_version_id: str,
    legal_document_id: str | None,
    source_type: str = "legal_handbook",
) -> list[DraftUnit]:
    from app.models.legal_handbook import LegalCitation, LegalUnit, LegalUnitChunk

    chunks = (
        db.query(LegalUnitChunk)
        .filter(LegalUnitChunk.legal_source_version_id == legal_source_version_id)
        .order_by(LegalUnitChunk.legal_unit_id, LegalUnitChunk.ordinal)
        .all()
    )
    out: list[DraftUnit] = []
    for i, ch in enumerate(chunks):
        unit = db.get(LegalUnit, ch.legal_unit_id)
        cites = (
            db.query(LegalCitation).filter(LegalCitation.legal_unit_chunk_id == ch.id).all()
        )
        cite_keys = [c.citation_key for c in cites]
        norm_cites = [c.normalized_citation for c in cites if c.normalized_citation]
        heading = (unit.heading_raw if unit else None) or ""
        body = ch.body_text or ""
        source_text = body.strip()
        if not source_text:
            continue

        sig = extract_signals(source_text, heading)
        utype, action, rlevel = _classify_unit(sig, source_text)
        conf = confidence_for_keyword_rules(
            matched_rules=sig.matched_rule_count, text_len=len(source_text)
        )

        exc_text = (source_text[:4000] if utype == UT.UNIT_EXCEPTION else None)
        esc_text = (source_text[:4000] if utype == UT.UNIT_ESCALATION_RULE else None)

        anchor = {
            "legal_unit_id": ch.legal_unit_id,
            "legal_unit_chunk_id": ch.id,
            "primary_citation": unit.primary_citation if unit else None,
            "page_start": ch.page_start,
            "page_end": ch.page_end,
        }
        facets: dict[str, Any] = {
            "extraction": "keyword_rules_v1",
            "signals": {
                "definition_like": sig.is_definition_like,
                "prohibition": sig.is_prohibition,
                "exception_like": sig.is_exception_like,
            },
        }
        headline = (heading[:200] if heading else None) or (norm_cites[0] if norm_cites else f"chunk-{i}")
        retrieval_blob = " ".join(
            x for x in [heading, norm_cites[0] if norm_cites else "", first_sentence(source_text)] if x
        )

        out.append(
            DraftUnit(
                ordinal=len(out),
                normalized_unit_type=utype,
                title=heading[:500] if heading else None,
                source_text=source_text,
                plain_language_summary=first_sentence(source_text) or None,
                applies_to_role=None,
                action_type=action,
                requirement_level=rlevel if rlevel != "unknown" else None,
                condition_text=None,
                exception_text=exc_text if utype == UT.UNIT_EXCEPTION else None,
                escalation_text=esc_text if utype == UT.UNIT_ESCALATION_RULE else None,
                output_outcome_text=None,
                citation_keys_json=json.dumps(cite_keys, ensure_ascii=False),
                anchor_json=json.dumps(anchor, ensure_ascii=False, sort_keys=True),
                structured_facets_json=json.dumps(facets, ensure_ascii=False, sort_keys=True),
                confidence_level=conf,
                legal_unit_id=ch.legal_unit_id,
                legal_unit_chunk_id=ch.id,
                legal_document_id=legal_document_id,
                legal_source_version_id=legal_source_version_id,
                retrieval_headline=headline[:500] if headline else None,
                retrieval_blob=retrieval_blob[:8000] if retrieval_blob else None,
                meta_json=json.dumps({"profile": "legal_handbook_v1"}, ensure_ascii=False),
            )
        )
    return out
