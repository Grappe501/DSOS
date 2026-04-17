"""Regression tests for Arkansas handbook A–H family boundary logic (no PDF binary)."""

from app.services.legal_ingestion.family_boundary import (
    RawFamilyHit,
    handbook_body_anchor_char,
    infer_family_code_from_title,
    _zone_for_family_hit,
    first_statute_line_char,
    reconcile_arkansas_family_hits,
)
from app.services.legal_ingestion.toc_parser import FamilySpan, parse_family_spans


def test_family_heading_without_dot_leaders_is_body_even_before_first_statute():
    text = (
        "COVER\n\n"
        "A. Pharmacy Practice Act (May 2023)\n"
        "17-92-101 Short title\n"
        "Body under A.\n"
    )
    st = first_statute_line_char(text)
    pos = text.index("A. Pharmacy")
    assert st is not None
    assert _zone_for_family_hit(text, pos, st) == "body"


def test_toc_dot_leader_line_is_toc_zone_before_statute():
    text = "A. Pharmacy Practice Act (May 2023) .... 12\n17-92-101 Short title\n"
    st = first_statute_line_char(text)
    pos = text.index("A. Pharmacy")
    assert _zone_for_family_hit(text, pos, st) == "toc"


def test_reconcile_prefers_body_anchor_over_toc_for_same_code():
    toc_block = "A. Pharmacy Practice Act (May 2023) .... 10\n"
    body_block = (
        "17-92-101 Short title\n\n"
        "A. Pharmacy Practice Act (May 2023)\n"
        "Statute text continues here with enough length.\n"
    )
    text = toc_block + "\n" + body_block
    bs = first_statute_line_char(text)
    resolved, notes = reconcile_arkansas_family_hits(text, body_start=bs)
    assert resolved
    a_hit = next(h for h in resolved if h.family_code == "A")
    assert a_hit.zone == "body"
    assert notes["per_code"]["A"]["toc_char_start"] < notes["per_code"]["A"]["body_char_start"]


def test_parse_family_spans_merges_ordered_spans_with_end_boundaries():
    parts = []
    for letter, title in (
        ("A", "Pharmacy Practice Act (May 2023)"),
        ("B", "Miscellaneous Statutes Related to Pharmacy (Jan 2020)"),
        ("C", "Uniform Controlled Substances Act (July 2022)"),
        ("D", "Insurance Policies – Prescription Drug Benefits (Jan 2021)"),
        ("E", "Food, Drug, and Cosmetic Act (March 2019)"),
        ("F", "Controlled Substances and Legend Drugs (Feb 2024)"),
        ("G", "Administrative Procedure Act (Jan 2018)"),
        ("H", "Rules Pertaining to Arkansas Prescription Drug Monitoring Program (Aug 2025)"),
    ):
        parts.append(f"{letter}. {title}\n\n17-1-1 Placeholder\nText.\n\n")
    text = "TOC\n" + "".join(parts)
    spans = parse_family_spans(text)
    assert len(spans) == 8
    ordered = sorted(spans, key=lambda s: s.char_start)
    for i, sp in enumerate(ordered):
        assert sp.char_end > sp.char_start
        if i + 1 < len(ordered):
            assert sp.char_end == ordered[i + 1].char_start
    assert {s.family_code for s in spans} == set("ABCDEFGH")
    assert all(isinstance(s, FamilySpan) for s in spans)
    assert all(s.span_provenance for s in spans)


def test_december_2025_style_toc_trailing_letter_and_body_anchors():
    """ASBP PDFs often use ``Title … B`` in the TOC and ``B Title`` in the body (not ``B.``)."""
    text = (
        "Table of Contents\n"
        "Pharmacy Practice Act A\n"
        "Miscellaneous Statutes Related to Pharmacy B\n"
        "Uniform Controlled Substances Act C\n"
        "Insurance Policies – Prescription Drug Benefits D\n"
        "Food, Drug, and Cosmetic Act E\n"
        "Controlled Substances and Legend Drugs F\n"
        "Administrative Procedure Act G\n"
        "Rules Pertaining to Arkansas Prescription Drug H\n"
        "Monitoring Program\n"
        "1\nArkansas State Board of Pharmacy Law Book\n"
        "Pharmacy Practice Act May 2023\n"
        "A Pharmacy Practice Act\n\n"
        "17-92-101. Definitions.\n\n"
        "B Miscellaneous Statutes Related to Pharmacy\n\n"
        "17-1-1. Placeholder.\n"
    )
    assert handbook_body_anchor_char(text) is not None
    assert infer_family_code_from_title("F Administrative Procedure Act") == "G"
    resolved, notes = reconcile_arkansas_family_hits(text, body_start=None)
    assert len(resolved) >= 6
    assert notes["detection_layers"]["toc_trailing_letter"] >= 6


def test_family_span_provenance_toc_only_is_low_confidence():
    hit = RawFamilyHit(
        family_code="A",
        title="Pharmacy Practice Act",
        embedded_revision=None,
        char_start=10,
        zone="toc",
    )
    from app.services.legal_ingestion.toc_parser import _provenance_for_code

    prov, conf, _notes = _provenance_for_code(
        "A",
        hit,
        {"A": {"note": "toc_only_no_body_heading", "toc_char_start": 10}},
    )
    assert prov == "toc_only"
    assert conf == "low"
