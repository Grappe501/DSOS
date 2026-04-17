"""
Purpose:
    Interpret `legal_date_layers` for user-facing “as of” explanations relative to the
    compiled edition (November 2025) vs embedded act dates (May 2023, August 2025).

Role in Malone:
    Clarifies which textual snapshot the handbook reflects—not statutory filing outside PDF.

Expected inputs:
    Date layer rows for document, family, or unit.

Expected outputs:
    Structured summary for `answer_formatter` and traces.

TODO boundary:
    Does not compute real-world legal effectiveness from government systems.
"""

from __future__ import annotations
