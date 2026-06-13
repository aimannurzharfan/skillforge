"""Offline retrieval over the seed corpus.

Each seed doc is split into paragraphs. A query is scored against every
paragraph by weighted term overlap, and the best paragraphs are returned as
citable passages. This runs with no network access and is the default backend.
"""

from __future__ import annotations

import re
from functools import lru_cache

from ..config import SEED_CORPUS_DIR
from .interface import Passage

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is",
    "are", "be", "by", "as", "at", "it", "its", "that", "this", "from", "into",
    "than", "then", "so", "but", "not", "can", "you", "your", "they", "their",
    "how", "what", "when", "which", "each", "one", "two", "more", "most", "use",
    "used", "using", "uses", "between", "across", "rather", "often", "many",
}


def _tokens(text: str) -> list[str]:
    return [t for t in _WORD.findall(text.lower()) if t not in _STOPWORDS and len(t) > 1]


def get_grounding_text(competency_id: str) -> str:
    """Concatenated prose of the docs that ground a competency.

    Used by the deterministic assessment fallback to score an answer against the
    material it should reflect.
    """
    from ..domain import load_catalog

    topic = load_catalog().topic(competency_id)
    if topic is None:
        return ""
    wanted = set(topic.source_docs)
    parts = [
        " ".join(doc["paragraphs"]) for doc in _load_docs() if doc["doc_id"] in wanted
    ]
    return " ".join(parts)


@lru_cache(maxsize=1)
def _load_docs() -> list[dict]:
    docs = []
    for path in sorted(SEED_CORPUS_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        title = path.stem
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
        blocks = [b.strip() for b in re.split(r"\n\s*\n", raw) if b.strip()]
        paragraphs = []
        for block in blocks:
            # Drop a leading H1 line; keep the prose of each paragraph.
            text = re.sub(r"^#+\s.*\n?", "", block).strip()
            if text and not text.startswith("#"):
                paragraphs.append(text)
        docs.append({"doc_id": path.stem, "title": title, "paragraphs": paragraphs})
    return docs


class LocalBackend:
    name = "local"

    def retrieve(self, query: str, k: int = 3, doc_ids: list[str] | None = None) -> list[Passage]:
        query_terms = _tokens(query)
        if not query_terms:
            return []
        query_set = set(query_terms)

        allowed = set(doc_ids) if doc_ids else None
        scored: list[Passage] = []
        for doc in _load_docs():
            if allowed is not None and doc["doc_id"] not in allowed:
                continue
            for para in doc["paragraphs"]:
                para_tokens = _tokens(para)
                if not para_tokens:
                    continue
                para_set = set(para_tokens)
                overlap = query_set & para_set
                if not overlap:
                    continue
                # Coverage of the query plus a small bonus for repeated hits.
                coverage = len(overlap) / len(query_set)
                density = sum(para_tokens.count(t) for t in overlap) / len(para_tokens)
                score = coverage + 0.25 * density
                scored.append(
                    Passage(
                        doc_id=doc["doc_id"],
                        title=doc["title"],
                        text=para,
                        score=score,
                        source=self.name,
                    )
                )

        scored.sort(key=lambda p: p.score, reverse=True)
        return scored[:k]
