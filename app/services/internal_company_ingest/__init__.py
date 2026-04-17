"""Deterministic discovery, classification, and orchestration for internal company knowledge intake."""

from __future__ import annotations

from app.services.internal_company_ingest.orchestration import run_internal_company_batch

__all__ = ["run_internal_company_batch"]
