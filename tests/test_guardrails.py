"""Guardrails: the safety gates are real and enforced.

Covers the invariants the orchestrator and planner rely on: an invented citation
is dropped, an out-of-taxonomy competency or role is rejected, a non-answer level
is coerced to none, and an invalid model payload makes the agent fall back to
deterministic text rather than trusting it.
"""

from __future__ import annotations

from skillforge import guardrails
from skillforge.agents import learning_planner
from skillforge.domain import load_catalog
from skillforge.knowledge.interface import Passage
from skillforge.orchestrator import Orchestrator


def test_invented_citation_is_dropped():
    citations = [
        {"doc_id": "04-routing-and-ospf", "title": "Routing", "text": "real"},
        {"doc_id": "made-up-source", "title": "Invented", "text": "hallucinated"},
    ]
    kept = guardrails.ground_citations(citations, ["04-routing-and-ospf"])
    assert [c["doc_id"] for c in kept] == ["04-routing-and-ospf"]


def test_out_of_taxonomy_competency_is_rejected():
    catalog = load_catalog()
    role = catalog.role("network_engineer")
    assert guardrails.is_known_competency(role, "routing")
    assert not guardrails.is_known_competency(role, "quantum_teleportation")


def test_unknown_role_is_rejected():
    catalog = load_catalog()
    assert guardrails.is_known_role(catalog, "network_engineer")
    assert not guardrails.is_known_role(catalog, "ceo")


def test_non_answer_level_is_coerced_to_none():
    assert guardrails.enforce_assessed_level("working") == "working"
    assert guardrails.enforce_assessed_level("") == "none"
    assert guardrails.enforce_assessed_level(None) == "none"
    assert guardrails.enforce_assessed_level("guru") == "none"
    assert guardrails.enforce_assessed_level("  Proficient ") == "proficient"


def test_invalid_model_json_falls_back(monkeypatch):
    """When the model is configured but returns junk, the planner stays grounded."""
    from skillforge.foundry_client import ModelUnavailable

    monkeypatch.setattr(learning_planner, "is_configured", lambda: True)

    def boom(*args, **kwargs):  # noqa: ARG001
        raise ModelUnavailable("model did not return valid JSON")

    monkeypatch.setattr(learning_planner, "chat_json", boom)

    catalog = load_catalog()
    gap = _zero_readiness(catalog).gaps[0]
    passages = [
        Passage(doc_id="04-routing-and-ospf", title="Routing", text="OSPF picks lowest cost.", score=1.0, source="local")
    ]
    plan, mode = learning_planner._plan_for_gap(gap, passages)
    assert mode == "deterministic"
    assert plan["summary"]
    assert plan["modules"]


def test_guardrail_report_counts_pass_and_fail():
    report = guardrails.GuardrailReport()
    report.record("a", True)
    report.record("b", True)
    report.record("c", False)
    assert report.passed == 2
    assert report.total == 3
    assert report.summary == "2/3"


def test_run_report_passes_on_a_clean_offline_run():
    orch = Orchestrator()
    start = orch.start_assessment("network_engineer")
    answers = [
        {
            "competency_id": q["competency_id"],
            "question": q["question"],
            "answer": "OSPF uses cost from bandwidth and runs Dijkstra to pick the shortest path.",
        }
        for q in start["questions"]
    ]
    result = orch.complete_assessment("network_engineer", answers)
    report = result["guardrails"]
    assert report["total"] >= 5
    assert report["passed"] == report["total"]


def _zero_readiness(catalog):
    from skillforge.domain import compute_readiness

    role = catalog.role("network_engineer")
    attained = {c.id: 0 for c in role.competencies}
    return compute_readiness(role, attained, set(attained))
