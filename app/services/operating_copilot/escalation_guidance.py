"""Escalation and stop-workflow lines from decision workflow."""

from __future__ import annotations

from typing import Any


def build_escalation_lines(decision_workflow: dict[str, Any] | None) -> list[str]:
    dw = decision_workflow or {}
    out: list[str] = []
    for e in (dw.get("escalations") or [])[:12]:
        k = e.get("kind") or "note"
        txt = (e.get("text") or "").strip()
        if txt:
            out.append(f"[{k}] {txt[:900]}")
    return out


def build_exception_lines(decision_workflow: dict[str, Any] | None) -> list[str]:
    dw = decision_workflow or {}
    out: list[str] = []
    for e in (dw.get("exceptions") or [])[:12]:
        txt = (e.get("text") or "").strip()
        if txt:
            out.append(txt[:900])
    return out


def build_condition_lines(decision_workflow: dict[str, Any] | None) -> list[str]:
    dw = decision_workflow or {}
    out: list[str] = []
    for c in (dw.get("conditions") or [])[:12]:
        txt = (c.get("text") or "").strip()
        if txt:
            out.append(txt[:900])
    return out
