"""Foundry IQ retrieval through the Azure AI Search knowledge base.

The knowledge base ``skillforge-network`` is queried with the GA *retrieve*
action in extractive mode (no LLM, no answer synthesis): a POST to
``{search-endpoint}/knowledgebases/{kb}/retrieve`` with an ``intents`` body. The
verified call shape and response layout come from the Azure AI Search docs
(api-version 2026-04-01). The response carries a JSON-encoded list of chunks,
each with a ref id, title, and content, which we turn into citable passages.

Authentication is either a search api-key (FOUNDRY_IQ_SEARCH_KEY) or, failing
that, an Entra ID bearer token for the search scope. On any error the backend
logs one clear warning to stderr and falls back to the local corpus.
"""

from __future__ import annotations

import json
import sys

import requests

from ..config import SETTINGS
from .interface import KnowledgeBackend, Passage

_SEARCH_SCOPE = "https://search.azure.com/.default"
_TIMEOUT = 30


class FoundryIQBackend:
    name = "foundry_iq"

    def __init__(self, fallback: KnowledgeBackend) -> None:
        self._fallback = fallback
        self._warned = False
        self._aad_token: str | None = None

    def _warn(self, message: str) -> None:
        # One clear warning per process is enough; do not spam the logs.
        if not self._warned:
            print(f"[skillforge] Foundry IQ unavailable, using local corpus: {message}", file=sys.stderr)
            self._warned = True

    def _auth_headers(self) -> dict[str, str]:
        if SETTINGS.foundry_iq_search_key:
            return {"api-key": SETTINGS.foundry_iq_search_key}
        # No key: try an Entra ID token (works when the host has a logged-in
        # identity with the Search Index Data Reader role).
        if self._aad_token is None:
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
            self._aad_token = credential.get_token(_SEARCH_SCOPE).token
        return {"Authorization": f"Bearer {self._aad_token}"}

    def _retrieve_url(self) -> str:
        endpoint = SETTINGS.foundry_iq_search_endpoint.rstrip("/")
        kb = SETTINGS.foundry_iq_knowledge_base
        return f"{endpoint}/knowledgebases/{kb}/retrieve?api-version={SETTINGS.foundry_iq_api_version}"

    def retrieve(self, query: str, k: int = 3, doc_ids: list[str] | None = None) -> list[Passage]:
        if not SETTINGS.foundry_iq_is_configured:
            self._warn("FOUNDRY_IQ_SEARCH_ENDPOINT or knowledge base not set")
            return self._fallback.retrieve(query, k, doc_ids)

        try:
            headers = {"Content-Type": "application/json", **self._auth_headers()}
            body = {"intents": [{"type": "semantic", "search": query}]}
            response = requests.post(self._retrieve_url(), headers=headers, json=body, timeout=_TIMEOUT)
            response.raise_for_status()
            passages = _parse_passages(response.json(), self.name)
        except Exception as exc:  # network, auth, parse, anything
            self._warn(str(exc))
            return self._fallback.retrieve(query, k, doc_ids)

        if not passages:
            # The KB answered but had nothing usable; stay grounded via local.
            self._warn("retrieve returned no passages")
            return self._fallback.retrieve(query, k, doc_ids)

        if doc_ids:
            allowed = set(doc_ids)
            filtered = [p for p in passages if p.doc_id in allowed]
            if filtered:
                passages = filtered
        return passages[:k]


def _parse_passages(payload: dict, source: str) -> list[Passage]:
    """Turn a retrieve response into passages.

    The extracted response is a chat-style message whose text is a JSON-encoded
    list of chunks: ``[{"ref_id","title","content", ...}]``.
    """
    passages: list[Passage] = []
    response = payload.get("response") or []
    for message in response:
        for part in message.get("content", []):
            if part.get("type") != "text":
                continue
            try:
                chunks = json.loads(part.get("text", ""))
            except (json.JSONDecodeError, TypeError):
                continue
            for rank, chunk in enumerate(chunks):
                if not isinstance(chunk, dict):
                    continue
                content = (chunk.get("content") or "").strip()
                if not content:
                    continue
                title = (chunk.get("title") or "").strip() or f"reference {chunk.get('ref_id', rank)}"
                passages.append(
                    Passage(
                        doc_id=_doc_id_for(title, chunk.get("ref_id")),
                        title=title,
                        text=content,
                        score=1.0 / (rank + 1),
                        source=source,
                    )
                )
    return passages


def _doc_id_for(title: str, ref_id: object) -> str:
    """Best-effort stable doc id from a chunk title; falls back to the ref id."""
    slug = title.lower().replace("&", "and")
    slug = "".join(ch if ch.isalnum() else "-" for ch in slug)
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or f"ref-{ref_id}"
