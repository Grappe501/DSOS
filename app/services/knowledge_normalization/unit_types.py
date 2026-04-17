"""Normalized unit type taxonomy (extensible strings)."""

from __future__ import annotations

# Core cross-domain
UNIT_DEFINITION = "definition"
UNIT_REQUIREMENT = "requirement"
UNIT_PROHIBITION = "prohibition"
UNIT_PERMISSION = "permission"
UNIT_EXCEPTION = "exception"
UNIT_ESCALATION_RULE = "escalation_rule"
UNIT_WORKFLOW_STEP = "workflow_step"
UNIT_DOCUMENTATION_RULE = "documentation_rule"
UNIT_REPORTING_RULE = "reporting_rule"
UNIT_CONTACT_REFERENCE = "contact_reference"
UNIT_DECISION_LOG_ENTRY = "decision_log_entry"
UNIT_POLICY_RULE = "policy_rule"
UNIT_GENERAL = "general_statement"

NORMALIZED_UNIT_TYPES = frozenset(
    {
        UNIT_DEFINITION,
        UNIT_REQUIREMENT,
        UNIT_PROHIBITION,
        UNIT_PERMISSION,
        UNIT_EXCEPTION,
        UNIT_ESCALATION_RULE,
        UNIT_WORKFLOW_STEP,
        UNIT_DOCUMENTATION_RULE,
        UNIT_REPORTING_RULE,
        UNIT_CONTACT_REFERENCE,
        UNIT_DECISION_LOG_ENTRY,
        UNIT_POLICY_RULE,
        UNIT_GENERAL,
    }
)

ACTION_OBLIGATION = "obligation"
ACTION_PROHIBITION = "prohibition"
ACTION_PERMISSION = "permission"
ACTION_RECOMMENDATION = "recommendation"
ACTION_DISCRETION = "discretion"
ACTION_UNKNOWN = "unknown"

REQUIREMENT_LEVEL_MUST = "must"
REQUIREMENT_LEVEL_SHOULD = "should"
REQUIREMENT_LEVEL_MAY = "may"
REQUIREMENT_LEVEL_UNKNOWN = "unknown"
