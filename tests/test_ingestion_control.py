"""Tests for business ingestion control plane (policy profile + validation helpers)."""

from __future__ import annotations

import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base


def _memory_session():
    import app.models.ingestion_control  # noqa: F401
    import app.models.legal_handbook  # noqa: F401
    import app.models.models  # noqa: F401

    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    return sessionmaker(bind=eng)()


def test_split_markdown_sections():
    from app.services.ingestion_control.ingest_runner import _split_markdownish_sections

    text = "# A\nintro\n\n## B\nbody"
    parts = _split_markdownish_sections(text)
    assert len(parts) >= 2
    assert any(p[0] == "A" for p in parts)


def test_policy_manual_ingest_end_to_end():
    from app.models.ingestion_control import IngestionSegment, IngestionSourceVersion
    from app.services.ingestion_control.ingest_runner import run_business_ingest
    from app.services.ingestion_control.parser_profiles import PROFILE_POLICY_MANUAL

    db = _memory_session()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Policy\nDo the right thing.\n\n# Details\nMore text.\n")
        path = f.name
    try:
        out = run_business_ingest(
            db,
            stable_key="TEST_POLICY_1",
            source_type="policy_manual",
            parser_profile_key=PROFILE_POLICY_MANUAL,
            source_path=path,
            title="Test Policy",
            version_label="v1",
            promotion_mode="if_pass",
            dimensional_tags={"domain": "Compliance", "role": "Staff"},
        )
        assert out.get("status") == "completed"
        assert out.get("validation_status") == "PASS"
        vid = out.get("ingestion_source_version_id")
        assert vid
        ver = db.query(IngestionSourceVersion).filter(IngestionSourceVersion.id == vid).one()
        assert ver.status == "promoted_active"
        segs = db.query(IngestionSegment).filter(IngestionSegment.ingestion_source_version_id == vid).all()
        assert len(segs) >= 1
    finally:
        import os

        os.unlink(path)


def test_validation_legal_counts_empty():
    from app.services.ingestion_control.validation import legal_version_counts

    db = _memory_session()
    counts = legal_version_counts(db, legal_source_version_id="nonexistent-version")
    assert counts["chunk_count"] == 0
