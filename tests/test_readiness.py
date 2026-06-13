"""Readiness math and score aggregation: the authoritative deterministic core."""

from __future__ import annotations

from skillforge.domain import (
    aggregate_scores,
    competency_coverage,
    compute_readiness,
    level_to_value,
    load_catalog,
    value_to_level,
)


def test_level_round_trip_and_clamping():
    for name in ["none", "aware", "working", "proficient"]:
        assert value_to_level(level_to_value(name)) == name
    assert value_to_level(-3) == "none"
    assert value_to_level(99) == "proficient"


def test_coverage_caps_at_one():
    assert competency_coverage(3, 2) == 1.0
    assert competency_coverage(1, 2) == 0.5
    assert competency_coverage(0, 3) == 0.0
    assert competency_coverage(2, 0) == 1.0


def test_aggregate_scores_averages_and_rounds():
    scored = [
        {"competency_id": "routing", "level": "working"},
        {"competency_id": "routing", "level": "proficient"},
        {"competency_id": "acls", "level": "aware"},
    ]
    attained = aggregate_scores(scored)
    # mean(working=2, proficient=3) = 2.5; Python round() is banker's rounding -> 2.
    assert attained["routing"] == 2
    assert attained["acls"] == 1


def test_full_marks_yields_100_percent():
    catalog = load_catalog()
    role = catalog.role("network_engineer")
    attained = {c.id: c.target_value for c in role.competencies}
    result = compute_readiness(role, attained, set(attained))
    assert result.readiness_percent == 100
    assert len(result.gaps) == 0
    assert len(result.strengths) == len(role.competencies)


def test_zero_knowledge_yields_zero_percent():
    catalog = load_catalog()
    role = catalog.role("network_engineer")
    attained = {c.id: 0 for c in role.competencies}
    result = compute_readiness(role, attained, set(attained))
    assert result.readiness_percent == 0
    assert len(result.gaps) == len(role.competencies)


def test_readiness_uses_only_assessed_competencies():
    catalog = load_catalog()
    role = catalog.role("network_engineer")
    # Only one competency assessed, at target; readiness should be 100 over the
    # assessed subset, not diluted by the unassessed ones.
    one = role.competencies[0]
    attained = {one.id: one.target_value}
    result = compute_readiness(role, attained, {one.id})
    assert result.readiness_percent == 100
    assessed = [c for c in result.competencies if c.assessed]
    assert len(assessed) == 1


def test_partial_coverage_is_weighted():
    catalog = load_catalog()
    role = catalog.role("network_engineer")
    # Use only competencies whose target is exactly "working" (value 2) and grant
    # half of it (value 1). Coverage is 0.5 on each, so renormalised readiness = 50.
    working_comps = [c for c in role.competencies if c.target_value == 2]
    assert working_comps, "expected some working-target competencies"
    attained = {c.id: 1 for c in working_comps}
    result = compute_readiness(role, attained, set(attained))
    assert result.readiness_percent == 50
