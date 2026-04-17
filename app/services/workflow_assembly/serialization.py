"""JSON-safe workflow assembly payloads."""

from __future__ import annotations

import json
from typing import Any


def dumps_assembly(obj: Any) -> dict[str, Any]:
    return json.loads(json.dumps(obj, default=str, ensure_ascii=False))
