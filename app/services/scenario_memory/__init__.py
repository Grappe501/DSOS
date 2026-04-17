"""Scenario memory + decision trace (audit / comparison; secondary to current evidence)."""

from __future__ import annotations

from app.services.scenario_memory.fallback import malone_scenario_memory_enabled, malone_scenario_memory_priors_enabled
from app.services.scenario_memory.precedence import PRECEDENCE_NOTE, current_evidence_outranks_memory
from app.services.scenario_memory.retrieval import attach_prior_scenario_context, find_prior_scenario_analogs
from app.services.scenario_memory.scenario_comparator import compare_to_prior_row
from app.services.scenario_memory.scenario_store import is_eligible_for_scenario_memory, persist_scenario_memory_and_trace

__all__ = [
    "attach_prior_scenario_context",
    "compare_to_prior_row",
    "current_evidence_outranks_memory",
    "find_prior_scenario_analogs",
    "is_eligible_for_scenario_memory",
    "malone_scenario_memory_enabled",
    "malone_scenario_memory_priors_enabled",
    "persist_scenario_memory_and_trace",
    "PRECEDENCE_NOTE",
]
