"""Local (offline) retrieval over the seed corpus."""

from __future__ import annotations

from skillforge.domain import load_catalog
from skillforge.knowledge import get_backend
from skillforge.knowledge.local_backend import get_grounding_text


def test_default_backend_is_local():
    backend = get_backend("local")
    assert backend.name == "local"


def test_retrieve_returns_ranked_passages():
    backend = get_backend("local")
    passages = backend.retrieve("VLSM subnetting CIDR prefix length", k=3)
    assert passages
    assert passages[0].score >= passages[-1].score
    assert all(p.source == "local" for p in passages)
    assert all(p.citation for p in passages)


def test_doc_id_filter_restricts_sources():
    backend = get_backend("local")
    passages = backend.retrieve(
        "subnet mask VLSM prefix length hosts", k=3, doc_ids=["02-ip-addressing-subnetting"]
    )
    assert passages
    assert {p.doc_id for p in passages} == {"02-ip-addressing-subnetting"}


def test_every_competency_query_grounds_in_its_docs():
    catalog = load_catalog()
    backend = get_backend("local")
    for cid, topic in catalog.topics.items():
        passages = backend.retrieve(topic.query, k=2, doc_ids=topic.source_docs)
        assert passages, f"no passages for {cid}"
        assert all(p.doc_id in topic.source_docs for p in passages)


def test_empty_query_returns_nothing():
    backend = get_backend("local")
    assert backend.retrieve("   ", k=3) == []


def test_grounding_text_present_for_each_competency():
    catalog = load_catalog()
    for cid in catalog.topics:
        assert get_grounding_text(cid).strip()
