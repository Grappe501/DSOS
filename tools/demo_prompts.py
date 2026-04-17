"""
Deterministic demo prompt set for owner-facing walkthroughs.

Use these strings in Malone chat (same path as production). Intent routing may require
[legal], [policy], or [sop] hints depending on environment and corpus.
"""

from __future__ import annotations

# Flow 1 — operational Q&A (policy / SOP / cross-source)
OPERATIONAL_QA_PROMPTS: tuple[str, ...] = (
    "What should we do if a prescription is missing required information?",
    "[policy] How do we handle PHI when coordinating with a prescriber?",
    "[sop] Walk me through the intake process for new patients.",
    "Who handles prior authorization and when do we escalate?",
)

# Flow 2 — inspection is UI-driven (telemetry / trace); no dedicated chat string required.
INSPECTION_NOTE: str = (
    "After a turn, open 'Show read-only inspection' and optionally load persisted trace."
)

# Flow 3 — department intake starter (also available as UI presets when MALONE_DEMO_MODE is on)
DEPARTMENT_INTAKE_STARTERS: tuple[str, ...] = (
    "Let’s map the pharmacy intake process: receiving new prescriptions and verifying patient identity.",
    "Map prior authorization: intake, payer rules, and escalation to the pharmacist on duty.",
)

# Cross-source scenario (may require cross-source decision feature enabled)
CROSS_SOURCE_PROMPT: str = (
    "[legal] [policy] When handbook rules and internal policy both apply, how should staff reconcile them?"
)


def all_demo_prompts() -> list[str]:
    return list(OPERATIONAL_QA_PROMPTS) + list(DEPARTMENT_INTAKE_STARTERS) + [CROSS_SOURCE_PROMPT]
