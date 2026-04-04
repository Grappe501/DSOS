from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.utils.logger import log


DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
DEFAULT_OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30"))
OPENAI_MAX_RENDER_CHARS = int(os.getenv("OPENAI_MAX_RENDER_CHARS", "2000"))
OPENAI_MAX_ITEMS_IN_PACKET = int(os.getenv("OPENAI_MAX_ITEMS_IN_PACKET", "25"))
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "2"))
OPENAI_ENABLE_WEB_SEARCH = os.getenv("OPENAI_ENABLE_WEB_SEARCH", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


class OpenAIServiceError(RuntimeError):
    pass


@dataclass(slots=True)
class RenderResult:
    provider: str
    model: str | None
    status: str
    clarification_needed: bool
    clarifying_question: str
    rendered_answer: str
    grounding_refs: list[str]
    source_refs: list[str]
    web_search_used: bool
    web_sources: list[dict[str, Any]]
    raw_response: dict[str, Any] | None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "status": self.status,
            "clarification_needed": self.clarification_needed,
            "clarifying_question": self.clarifying_question,
            "rendered_answer": self.rendered_answer,
            "grounding_refs": list(self.grounding_refs),
            "source_refs": list(self.source_refs),
            "web_search_used": self.web_search_used,
            "web_sources": list(self.web_sources),
            "duration_ms": self.duration_ms,
            "raw_response": None,
        }


RENDER_OUTPUT_SCHEMA: dict[str, Any] = {
    "name": "malone_render_response",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "clarification_needed": {"type": "boolean"},
            "clarifying_question": {"type": "string"},
            "rendered_answer": {"type": "string"},
            "grounding_refs": {
                "type": "array",
                "items": {"type": "string"},
            },
            "source_refs": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": [
            "clarification_needed",
            "clarifying_question",
            "rendered_answer",
            "grounding_refs",
            "source_refs",
        ],
        "additionalProperties": False,
    },
}


def is_openai_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def is_web_search_enabled() -> bool:
    return is_openai_enabled() and OPENAI_ENABLE_WEB_SEARCH


def _trim_truth_packet(packet: dict[str, Any]) -> dict[str, Any]:
    trimmed = dict(packet)

    deterministic_result = trimmed.get("deterministic_result")
    if isinstance(deterministic_result, dict):
        copied_result = dict(deterministic_result)

        items = copied_result.get("items")
        if isinstance(items, list):
            copied_result["items"] = items[:OPENAI_MAX_ITEMS_IN_PACKET]

        trimmed["deterministic_result"] = copied_result

    allowed_claims = trimmed.get("allowed_claims")
    if isinstance(allowed_claims, list):
        trimmed["allowed_claims"] = allowed_claims[: max(OPENAI_MAX_ITEMS_IN_PACKET + 10, 20)]

    return trimmed


def _extract_output_text(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    outputs = payload.get("output") or []
    for item in outputs:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message":
            continue

        for content_item in item.get("content") or []:
            if not isinstance(content_item, dict):
                continue
            if content_item.get("type") == "output_text":
                text = content_item.get("text")
                if isinstance(text, str) and text.strip():
                    return text

    return ""


def _post_json(*, url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=OPENAI_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise OpenAIServiceError(f"OpenAI HTTP {exc.code}: {error_body}") from exc
    except URLError as exc:
        raise OpenAIServiceError(f"OpenAI connectivity error: {exc}") from exc
    except TimeoutError as exc:
        raise OpenAIServiceError("OpenAI request timed out") from exc
    except json.JSONDecodeError as exc:
        raise OpenAIServiceError(f"OpenAI response JSON parse failure: {exc}") from exc


def _normalize_render_payload(parsed: dict[str, Any]) -> dict[str, Any]:
    clarification_needed = bool(parsed.get("clarification_needed"))
    clarifying_question = str(parsed.get("clarifying_question") or "").strip()
    rendered_answer = str(parsed.get("rendered_answer") or "").strip()

    grounding_refs = [
        str(value).strip()
        for value in (parsed.get("grounding_refs") or [])
        if str(value).strip()
    ]

    source_refs = [
        str(value).strip()
        for value in (parsed.get("source_refs") or [])
        if str(value).strip()
    ]

    if clarification_needed and not clarifying_question:
        clarifying_question = (
            "Could you clarify exactly which part of the system or workflow you want me to work with?"
        )

    if len(rendered_answer) > OPENAI_MAX_RENDER_CHARS:
        rendered_answer = rendered_answer[:OPENAI_MAX_RENDER_CHARS].rstrip()

    return {
        "clarification_needed": clarification_needed,
        "clarifying_question": clarifying_question,
        "rendered_answer": rendered_answer,
        "grounding_refs": grounding_refs,
        "source_refs": source_refs,
    }


def _recursive_collect_sources(value: Any, collected: list[dict[str, Any]]) -> None:
    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str) and url.strip():
            collected.append(
                {
                    "title": str(value.get("title") or "").strip(),
                    "url": url.strip(),
                    "publisher": str(value.get("publisher") or value.get("site_name") or "").strip(),
                    "snippet": str(value.get("snippet") or value.get("description") or "").strip(),
                }
            )
        for nested in value.values():
            _recursive_collect_sources(nested, collected)
        return

    if isinstance(value, list):
        for item in value:
            _recursive_collect_sources(item, collected)


def _extract_web_sources(payload: dict[str, Any]) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    _recursive_collect_sources(payload, collected)

    deduped: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for item in collected:
        url = str(item.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(
            {
                "title": item.get("title") or url,
                "url": url,
                "publisher": item.get("publisher") or "",
                "snippet": item.get("snippet") or "",
            }
        )

    return deduped[:10]


def render_conversational_response(
    *,
    truth_packet: dict[str, Any],
    allow_web_search: bool = False,
) -> RenderResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return RenderResult(
            provider="openai",
            model=None,
            status="disabled",
            clarification_needed=False,
            clarifying_question="",
            rendered_answer="",
            grounding_refs=[],
            source_refs=[],
            web_search_used=False,
            web_sources=[],
            raw_response=None,
            duration_ms=0,
        )

    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    base_url = os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL).rstrip("/")
    trimmed_truth_packet = _trim_truth_packet(truth_packet)
    web_enabled_for_request = bool(allow_web_search and is_web_search_enabled())

    developer_message = (
        "You are Malone's conversational rendering layer inside a governed operating system. "
        "You must only speak from the provided truth packet JSON and any web sources returned by the built-in web search tool when that tool is enabled. "
        "If the packet indicates ambiguity or insufficient deterministic support, set clarification_needed to true and ask one concise, high-value question. "
        "Return JSON only. Do not invent facts. Do not mention hidden reasoning. "
        "Use grounding_refs to list exact claim ids from allowed_claims that you used. "
        "If web search is available and needed, use source_refs to list the exact source URLs you relied on. "
        "If web search is not used, source_refs must be an empty array."
    )

    user_message = (
        "Render the final assistant response as structured JSON from this truth packet. "
        "If the user message is ambiguous, prefer a clarification question over guessing. "
        "If web search is enabled and the question requires current external information, search the web and cite the exact source URLs in source_refs.\n\n"
        f"TRUTH_PACKET_JSON:\n{json.dumps(trimmed_truth_packet, default=str)}"
    )

    payload: dict[str, Any] = {
        "model": model,
        "input": [
            {"role": "developer", "content": developer_message},
            {"role": "user", "content": user_message},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": RENDER_OUTPUT_SCHEMA["name"],
                "strict": True,
                "schema": RENDER_OUTPUT_SCHEMA["schema"],
            }
        },
    }

    if web_enabled_for_request:
        payload["tools"] = [{"type": "web_search"}]
        payload["include"] = ["web_search_call.action.sources"]

    started_at = time.time()
    last_error: Exception | None = None

    for attempt in range(1, max(OPENAI_MAX_RETRIES, 1) + 1):
        try:
            log(
                f"Malone OpenAI render request using model={model}, "
                f"attempt={attempt}, web_search={web_enabled_for_request}"
            )
            response_payload = _post_json(
                url=f"{base_url}/responses",
                api_key=api_key,
                payload=payload,
            )

            parsed_text = _extract_output_text(response_payload)
            if not parsed_text:
                raise OpenAIServiceError("OpenAI response did not include output text")

            try:
                parsed = json.loads(parsed_text)
            except json.JSONDecodeError as exc:
                raise OpenAIServiceError(f"OpenAI JSON parse failure: {exc}") from exc

            normalized = _normalize_render_payload(parsed)
            duration_ms = int((time.time() - started_at) * 1000)
            web_sources = _extract_web_sources(response_payload)
            web_search_used = bool(web_sources)

            return RenderResult(
                provider="openai",
                model=model,
                status="completed",
                clarification_needed=normalized["clarification_needed"],
                clarifying_question=normalized["clarifying_question"],
                rendered_answer=normalized["rendered_answer"],
                grounding_refs=normalized["grounding_refs"],
                source_refs=normalized["source_refs"],
                web_search_used=web_search_used,
                web_sources=web_sources,
                raw_response=response_payload,
                duration_ms=duration_ms,
            )
        except OpenAIServiceError as exc:
            last_error = exc
            if attempt >= max(OPENAI_MAX_RETRIES, 1):
                break
        except Exception as exc:
            last_error = OpenAIServiceError(f"Unexpected OpenAI render failure: {exc}")
            if attempt >= max(OPENAI_MAX_RETRIES, 1):
                break

    raise OpenAIServiceError(str(last_error) if last_error else "OpenAI render failed")