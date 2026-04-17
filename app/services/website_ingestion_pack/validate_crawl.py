"""Crawl run validation: PASS / PASS_WITH_WARNINGS / FAIL."""

from __future__ import annotations

from typing import Any


def validate_crawl_run(
    *,
    target_reachable: bool,
    inventory_count: int,
    manifests_written: bool,
    entries_by_type: dict[str, int],
    weak_unclassified_ratio: float,
) -> dict[str, Any]:
    """
    FAIL: cannot reach domain, empty inventory, no manifests, or unusably sparse classification.
    PASS_WITH_WARNINGS: crawl ok, manifests ok, some weakness.
    PASS: healthy inventory + manifests + materially useful mix.
    """
    failures: list[str] = []
    warnings: list[str] = []

    if not target_reachable:
        failures.append("target_domain_unreachable")
    if inventory_count < 3:
        failures.append("inventory_too_small")
    if not manifests_written:
        failures.append("manifests_not_written")
    if weak_unclassified_ratio > 0.95 and inventory_count > 30:
        failures.append("classification_unusably_sparse")

    if inventory_count > 0 and inventory_count < 10:
        warnings.append("inventory_below_ideal_diversity")
    if weak_unclassified_ratio > 0.35:
        warnings.append("many_items_weakly_classified_or_general_reference")
    if entries_by_type.get("general_reference", 0) > inventory_count * 0.6 and inventory_count > 10:
        warnings.append("general_reference_dominates")

    if failures:
        status = "FAIL"
    elif warnings:
        status = "PASS_WITH_WARNINGS"
    else:
        non_g = sum(1 for k, v in entries_by_type.items() if k != "general_reference" and v > 0)
        if inventory_count >= 12 and non_g >= 3:
            status = "PASS"
        elif inventory_count >= 8:
            status = "PASS_WITH_WARNINGS"
            warnings.append("pass_bar_not_met_for_full_pass")
        else:
            status = "PASS_WITH_WARNINGS"

    return {
        "overall_status": status,
        "failures": failures,
        "warnings": warnings,
        "rules_version": 1,
    }
