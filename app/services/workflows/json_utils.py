from __future__ import annotations
import json
from datetime import datetime
from typing import Any
def utcnow() -> datetime:
    return datetime.utcnow()
def normalize_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
def normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        return []
    out=[]; seen=set()
    for value in values:
        text = normalize_str(value)
        if text and text not in seen:
            out.append(text); seen.add(text)
    return out
def safe_json(value: Any, *, default: str="{}") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except Exception:
        return json.dumps({"raw": str(value)})
def coerce_json(value: str | None) -> Any:
    if value in (None, ""):
        return None
    try:
        return json.loads(value)
    except Exception:
        return value
def coerce_json_dict(value: str | None) -> dict[str, Any]:
    parsed = coerce_json(value)
    return parsed if isinstance(parsed, dict) else {}
def serialize_meta(meta: dict[str, Any] | None) -> str | None:
    if meta is None:
        return None
    try:
        return json.dumps(meta, default=str)
    except Exception:
        return str(meta)
def merge_context_dict(base: dict[str, Any] | None, updates: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(base or {})
    for key, value in (updates or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged
def actor_from_context(context: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(context, dict):
        return {}
    actor = context.get("actor")
    return actor if isinstance(actor, dict) else {}
def extract_actor_from_nested_context(context: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(context, dict):
        return {}
    actor = context.get("actor")
    if isinstance(actor, dict):
        return actor
    nested = context.get("context")
    if isinstance(nested, dict):
        nested_actor = nested.get("actor")
        if isinstance(nested_actor, dict):
            return nested_actor
    return {}
def actor_id(actor: dict[str, Any] | None) -> str | None:
    if not isinstance(actor, dict):
        return None
    return normalize_str(actor.get("id"))
def isoformat_or_none(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return value.isoformat()
    except Exception:
        return str(value)
def ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
def ensure_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
