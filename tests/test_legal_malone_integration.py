"""Legal evidence bundle, intent gating, and formatter (no external services)."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base


def _memory_db():
    import app.models.models  # noqa: F401
    import app.models.legal_handbook  # noqa: F401

    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    return sessionmaker(bind=eng)()


def test_format_legal_lookup_answer_empty():
    from app.services.legal_assistant.answer_formatter import format_legal_lookup_answer

    text = format_legal_lookup_answer([])
    assert "No matching excerpts" in text


def test_legal_intent_requires_env_flag(monkeypatch):
    from app.services.intent_service import classify_intent

    monkeypatch.delenv("MALONE_LEGAL_EVIDENCE_ENABLED", raising=False)
    t = classify_intent("What does Arkansas 17-92-101 say for ASBP?")
    assert t.get("target") == "general"

    monkeypatch.setenv("MALONE_LEGAL_EVIDENCE_ENABLED", "1")
    t2 = classify_intent("What does Arkansas 17-92-101 say for ASBP?")
    assert t2.get("target") == "legal_handbook"


def test_build_legal_evidence_bundle_scoped(monkeypatch):
    monkeypatch.setenv("MALONE_LEGAL_EVIDENCE_ENABLED", "1")
    from app.models.legal_handbook import (
        LegalCitation,
        LegalDocument,
        LegalDocumentFamily,
        LegalSourceVersion,
        LegalUnit,
        LegalUnitChunk,
    )
    from app.models.models import gen_id
    from app.services.legal_evidence_service import build_legal_evidence_bundle

    db = _memory_db()
    doc = LegalDocument(
        id=gen_id(),
        stable_key="test-doc",
        title="Test",
        cover_metadata_json="{}",
        meta_json="{}",
    )
    db.add(doc)
    db.flush()
    ver = LegalSourceVersion(
        id=gen_id(),
        legal_document_id=doc.id,
        version_label="v1",
        meta_json="{}",
    )
    db.add(ver)
    db.flush()
    fam = LegalDocumentFamily(
        id=gen_id(),
        legal_document_id=doc.id,
        family_code="A",
        title="Pharmacy Practice Act",
        sort_order=0,
        meta_json="{}",
    )
    db.add(fam)
    db.flush()
    unit = LegalUnit(
        id=gen_id(),
        legal_document_family_id=fam.id,
        unit_kind="section",
        primary_citation="17-92-101",
        heading_raw="Short title",
        ordinal=0,
        meta_json="{}",
    )
    db.add(unit)
    db.flush()
    ch = LegalUnitChunk(
        id=gen_id(),
        legal_unit_id=unit.id,
        legal_source_version_id=ver.id,
        ordinal=0,
        body_text="This is the short title statute text for testing retrieval.",
        retrieval_ready=True,
        page_start=12,
        page_end=12,
        meta_json="{}",
    )
    db.add(ch)
    db.flush()
    cite = LegalCitation(
        id=gen_id(),
        legal_unit_chunk_id=ch.id,
        citation_key="ARK-STAT-17-92-101",
        normalized_citation="17-92-101",
        anchor_json="{}",
    )
    db.add(cite)
    db.commit()

    bundle = build_legal_evidence_bundle(db, "17-92-101 short title", limit=5)
    assert bundle.get("legal_source_version_id") == ver.id
    assert len(bundle.get("items") or []) >= 1
    assert (bundle.get("items") or [{}])[0].get("legal_unit_chunk_id") == ch.id
