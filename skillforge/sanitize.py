"""Defenses for untrusted free text (the person's answers and any role input).

User text is always passed to the model as a separate user message, never spliced
into the system prompt or the grounding. These helpers add a second layer: they
cap length, strip control characters, and neutralise the most common prompt
injection phrasings so a pasted instruction cannot steer the model.
"""

from __future__ import annotations

import re

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\b.*?(instruction|prompt)s?"),
    re.compile(r"(?i)\bdisregard\s+(the\s+)?(previous|prior|above|system)\b"),
    re.compile(r"(?i)\byou\s+are\s+now\b"),
    re.compile(r"(?i)\bact\s+as\b.*?\b(system|developer|admin)\b"),
    re.compile(r"(?i)\bsystem\s*prompt\b"),
    re.compile(r"(?i)<\s*/?\s*(system|assistant|user)\s*>"),
]

DEFAULT_MAX_LEN = 2000


def sanitize_user_text(text: str | None, *, max_len: int = DEFAULT_MAX_LEN) -> str:
    """Return a cleaned, length-bounded copy of untrusted text."""
    if not isinstance(text, str):
        return ""
    cleaned = _CONTROL.sub(" ", text)
    for pattern in _INJECTION_PATTERNS:
        cleaned = pattern.sub("[removed]", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip() + " [truncated]"
    return cleaned


def sanitize_identifier(value: str | None, *, max_len: int = 120) -> str:
    """Restrict an identifier to a safe character set."""
    if not isinstance(value, str):
        return ""
    return re.sub(r"[^a-z0-9_\-]", "", value.strip().lower())[:max_len]
