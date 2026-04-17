"""Unit tests for Arkansas ingest QA status classification (narrow)."""

from __future__ import annotations

from app.services.legal_ingestion.ingest_validate_status import (
    decide_overall_status,
    retrieval_is_broad_failure,
)


def test_decide_overall_status_failures_win():
    assert decide_overall_status(["precheck"], ["warn"]) == "FAIL"


def test_decide_overall_status_warnings_only():
    assert decide_overall_status([], ["family"]) == "PASS_WITH_WARNINGS"


def test_decide_overall_status_clean_pass():
    assert decide_overall_status([], []) == "PASS"


def test_retrieval_broad_failure_empty_probes():
    assert retrieval_is_broad_failure([]) is True


def test_retrieval_broad_failure_all_zero():
    assert (
        retrieval_is_broad_failure(
            [{"hit_count": 0}, {"hit_count": 0}],
        )
        is True
    )


def test_retrieval_not_broad_if_any_hit():
    assert (
        retrieval_is_broad_failure(
            [{"hit_count": 0}, {"hit_count": 1}],
        )
        is False
    )
