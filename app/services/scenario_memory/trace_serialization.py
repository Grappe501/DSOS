"""JSON serialization for persisted traces (size-bounded, audit-friendly)."""

from __future__ import annotations

import json
from typing import Any

_MAX_TEXT = 450_000


def dumps_limited(obj: Any, *, max_chars: int = _MAX_TEXT) -> str:
    raw = json.dumps(obj, ensure_ascii=False, default=str)
    if len(raw) <= max_chars:
        return raw
    return json.dumps(
        {
            "_truncated": True,
            "_original_chars": len(raw),
            "preview": raw[: max_chars // 2],
        },
        ensure_ascii=False,
    )


def loads_safe(raw: str | None, default: Any) -> Any:
    if not raw or not str(raw).strip():
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default
