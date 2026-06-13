"""Retrieval interface shared by both knowledge backends.

A backend takes a natural-language query and returns ranked passages, each with
the source document it came from so the learning planner can cite it. The backend
is chosen by the KNOWLEDGE_BACKEND environment variable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..config import SETTINGS


@dataclass(frozen=True)
class Passage:
    doc_id: str
    title: str
    text: str
    score: float
    source: str  # "local" or "foundry_iq"

    @property
    def citation(self) -> str:
        return f"{self.title} ({self.doc_id})"

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "text": self.text,
            "score": round(self.score, 4),
            "source": self.source,
            "citation": self.citation,
        }


class KnowledgeBackend(Protocol):
    name: str

    def retrieve(self, query: str, k: int = 3, doc_ids: list[str] | None = None) -> list[Passage]:
        ...


def get_backend(name: str | None = None) -> KnowledgeBackend:
    """Return the configured backend.

    ``foundry_iq`` is wrapped so that any retrieval error falls back to the local
    corpus with a single clear warning, keeping the app usable offline.
    """
    name = (name or SETTINGS.knowledge_backend or "local").lower()
    from .local_backend import LocalBackend

    local = LocalBackend()
    if name == "foundry_iq":
        from .foundry_iq_backend import FoundryIQBackend

        return FoundryIQBackend(fallback=local)
    return local
