"""PASS / PASS_WITH_WARNINGS / FAIL for normalization runs (ingestion-style)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NormalizationValidationResult:
    overall: str  # PASS | PASS_WITH_WARNINGS | FAIL
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def decide_normalization_status(failures: list[str], warnings: list[str]) -> str:
    if failures:
        return "FAIL"
    if warnings:
        return "PASS_WITH_WARNINGS"
    return "PASS"


def validate_run_payload(
    *,
    source_resolved: bool,
    unit_count: int,
    orphan_chunk_links: int,
    missing_required_fields: int,
    profile_key: str,
) -> NormalizationValidationResult:
    failures: list[str] = []
    warnings: list[str] = []

    if not source_resolved:
        failures.append("source_selection_failed")

    if source_resolved and unit_count == 0:
        failures.append("no_normalized_units_produced")

    if orphan_chunk_links > 0:
        failures.append(f"orphan_source_links:{orphan_chunk_links}")

    if missing_required_fields > 0:
        warnings.append(f"missing_optional_structured_fields:{missing_required_fields}")

    if unit_count > 50000:
        warnings.append("very_large_normalization_run")

    overall = decide_normalization_status(failures, warnings)
    return NormalizationValidationResult(
        overall=overall,
        failures=failures,
        warnings=warnings,
        details={"profile_key": profile_key, "unit_count": unit_count},
    )
