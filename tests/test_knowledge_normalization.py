"""Tests for knowledge normalization (deterministic extractors + policy path)."""

from __future__ import annotations

import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base


def _memory_session():
    import app.models.ingestion_control  # noqa: F401
    import app.models.knowledge_normalization  # noqa: F401
    import app.models.legal_handbook  # noqa: F401
    import app.models.models  # noqa: F401

    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    return sessionmaker(bind=eng)()


def test_extract_signals_definition():
    from app.services.knowledge_normalization.field_extractors import extract_signals

    sig = extract_signals("(1) \"Drug\" means a substance.", "Definitions")
    assert sig.is_definition_like


def test_normalization_validation_pass():
    from app.services.knowledge_normalization.normalization_validation import validate_run_payload

    r = validate_run_payload(
        source_resolved=True,
        unit_count=3,
        orphan_chunk_links=0,
        missing_required_fields=0,
        profile_key="legal_handbook_v1",
    )
    assert r.overall == "PASS"


def test_policy_normalization_end_to_end():
    from app.models.ingestion_control import IngestionSource, IngestionSourceVersion
    from app.services.ingestion_control.parser_profiles import PROFILE_POLICY_MANUAL
    from app.services.ingestion_control.ingest_runner import run_business_ingest
    from app.services.knowledge_normalization.normalization_runner import run_normalization

    db = _memory_session()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Data Handling\nStaff must encrypt laptops.\n\n# Exceptions\nUnless approved by IT.\n")
        path = f.name
    try:
        out_ingest = run_business_ingest(
            db,
            stable_key="TEST_NORM_POLICY_1",
            source_type="policy_manual",
            parser_profile_key=PROFILE_POLICY_MANUAL,
            source_path=path,
            title="Test Policy",
            version_label="v1",
            promotion_mode="if_pass",
            dimensional_tags={},
        )
        assert out_ingest.get("status") == "completed"
        vid = out_ingest["ingestion_source_version_id"]
        src = db.query(IngestionSource).filter(IngestionSource.stable_key == "TEST_NORM_POLICY_1").one()
        norm = run_normalization(
            db,
            source_type="policy_manual",
            profile_key=None,
            legal_source_version_id=None,
            ingestion_source_version_id=vid,
            ingestion_source_id=src.id,
            legal_document_id=None,
        )
        assert norm.get("source_resolved") is True
        assert norm.get("unit_count", 0) >= 1
        assert norm.get("validation_status") in ("PASS", "PASS_WITH_WARNINGS")
    finally:
        import os

        os.unlink(path)
