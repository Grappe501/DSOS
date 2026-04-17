"""JSON helpers."""

from __future__ import annotations

import json
from typing import Any


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
