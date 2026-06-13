"""Client for Phi-4-mini-instruct on Microsoft Foundry.

The model is reached through the Foundry OpenAI-compatible endpoint using the
openai SDK. Every call runs in JSON mode at temperature 0 with a tight schema
and a one-shot example, supplied by the caller. When the model is not configured
or a call fails, the client raises ModelUnavailable and the calling agent falls
back to deterministic text.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .config import SETTINGS

# A focused budget. The model only writes short, structured language.
_MAX_TOKENS = 700
_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


class ModelUnavailable(RuntimeError):
    """Raised when the model cannot be reached or returned unusable output."""


def is_configured() -> bool:
    return SETTINGS.model_is_configured


_client = None


def _get_client():
    global _client
    if _client is None:
        if not is_configured():
            raise ModelUnavailable("Foundry model endpoint is not configured")
        from openai import OpenAI

        _client = OpenAI(
            base_url=SETTINGS.foundry_endpoint,
            api_key=SETTINGS.foundry_api_key,
        )
    return _client


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fenced = _FENCE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fall back to the first balanced object in the string.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def chat_json(
    system: str,
    user: str,
    *,
    example_user: str | None = None,
    example_assistant: str | None = None,
    max_tokens: int = _MAX_TOKENS,
) -> dict[str, Any]:
    """Run one JSON-mode completion and return the parsed object.

    Grounding and instructions go in ``system``; untrusted free text goes in
    ``user``. The optional one-shot example pins the output shape.
    """
    client = _get_client()

    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    if example_user and example_assistant:
        messages.append({"role": "user", "content": example_user})
        messages.append({"role": "assistant", "content": example_assistant})
    messages.append({"role": "user", "content": user})

    kwargs: dict[str, Any] = {
        "model": SETTINGS.foundry_model_deployment,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }

    try:
        try:
            response = client.chat.completions.create(
                response_format={"type": "json_object"}, **kwargs
            )
        except Exception:
            # Not every deployment honours response_format; retry plain and parse.
            response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
    except Exception as exc:  # network, auth, rate limit, etc.
        raise ModelUnavailable(str(exc)) from exc

    try:
        return _extract_json(content)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ModelUnavailable(f"model did not return valid JSON: {exc}") from exc
