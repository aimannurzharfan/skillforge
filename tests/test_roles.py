"""Role and competency mapping: the curated taxonomy must stay self-consistent."""

from __future__ import annotations

import math

from skillforge.config import SEED_CORPUS_DIR
from skillforge.domain import LEVEL_ORDER, load_catalog

EXPECTED_ROLES = {
    "network_engineer",
    "network_architect",
    "network_automation_engineer",
    "cloud_network_engineer",
    "noc_engineer",
    "wireless_network_engineer",
    "network_security_engineer",
    "soc_analyst",
}


def test_catalog_has_expected_roles():
    catalog = load_catalog()
    assert set(catalog.roles) == EXPECTED_ROLES


def test_weights_sum_to_one_per_role():
    catalog = load_catalog()
    for role in catalog.roles.values():
        total = sum(c.weight for c in role.competencies)
        assert math.isclose(total, 1.0, abs_tol=1e-9), f"{role.id} weights sum to {total}"


def test_target_levels_are_valid():
    catalog = load_catalog()
    for role in catalog.roles.values():
        for comp in role.competencies:
            assert comp.target_level in LEVEL_ORDER


def test_every_competency_maps_to_a_topic_and_existing_docs():
    catalog = load_catalog()
    doc_ids = {p.stem for p in SEED_CORPUS_DIR.glob("*.md")}
    for role in catalog.roles.values():
        for comp in role.competencies:
            topic = catalog.topic(comp.id)
            assert topic is not None, f"{comp.id} has no topic mapping"
            assert topic.source_docs, f"{comp.id} has no source docs"
            for doc in topic.source_docs:
                assert doc in doc_ids, f"{comp.id} cites missing doc {doc}"


def test_builds_on_points_to_a_real_role():
    catalog = load_catalog()
    for role in catalog.roles.values():
        if role.builds_on is not None:
            assert role.builds_on in catalog.roles


def test_shared_competency_ids_keep_consistent_names():
    catalog = load_catalog()
    names: dict[str, str] = {}
    for role in catalog.roles.values():
        for comp in role.competencies:
            if comp.id in names:
                assert names[comp.id] == comp.name, f"{comp.id} name differs across roles"
            else:
                names[comp.id] = comp.name
