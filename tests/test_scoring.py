"""Scoring scenarios: non-answers must score low, strong answers high.

These lock the fix for the bug where answering "not sure" to every question still
returned a high readiness. The end-to-end cases stub the assessor so the model's
verdict is controlled, which exercises the orchestrator's aggregation guard and
the readiness math; the offline cases exercise the real deterministic fallback.
"""

from __future__ import annotations

import pytest

from skillforge.agents import assessor
from skillforge.domain import aggregate_scores, compute_readiness, load_catalog
from skillforge.orchestrator import Orchestrator

# Answer text encodes the level the stubbed model should return, so each scenario
# is explicit about what the candidate demonstrated.
_STUB_LEVEL = {
    "NOT_SURE": ("none", 0),
    "EMPTY": ("none", 0),
    "STRONG": ("proficient", 90),
    "PARTIAL": ("aware", 35),
}


def _stub_evaluate_answer(role, competency, question, answer):  # noqa: ARG001
    level, score = _STUB_LEVEL.get(answer.strip(), ("none", 0))
    return {"level": level, "score": score, "rationale": "stubbed"}, "model"


def _answers_all(start, text):
    return [
        {"competency_id": q["competency_id"], "question": q["question"], "answer": text}
        for q in start["questions"]
    ]


@pytest.fixture
def stub_model(monkeypatch):
    monkeypatch.setattr(assessor, "evaluate_answer", _stub_evaluate_answer)


def test_not_sure_to_every_question_is_not_role_ready(stub_model):
    orch = Orchestrator()
    start = orch.start_assessment("network_engineer")
    result = orch.complete_assessment("network_engineer", _answers_all(start, "NOT_SURE"))
    assert result["readiness_percent"] < 30
    # Every assessed competency landed at none, never defaulted up.
    assert all(e["level"] == "none" for e in result["evaluations"])
    assessed = [c for c in result["competencies"] if c["assessed"]]
    assert all(not c["meets_target"] for c in assessed)


def test_empty_answers_are_not_role_ready(stub_model):
    orch = Orchestrator()
    start = orch.start_assessment("network_engineer")
    result = orch.complete_assessment("network_engineer", _answers_all(start, "EMPTY"))
    assert result["readiness_percent"] < 30


def test_strong_answers_are_role_ready(stub_model):
    orch = Orchestrator()
    start = orch.start_assessment("network_engineer")
    result = orch.complete_assessment("network_engineer", _answers_all(start, "STRONG"))
    assert result["readiness_percent"] > 70


def test_mixed_answers_land_in_between(stub_model):
    orch = Orchestrator()
    start = orch.start_assessment("network_engineer")
    answers = _answers_all(start, "STRONG")
    # Knock the two highest-weighted competencies down to a non-answer.
    answers[0]["answer"] = "NOT_SURE"
    answers[2]["answer"] = "NOT_SURE"
    result = orch.complete_assessment("network_engineer", answers)
    assert 30 <= result["readiness_percent"] <= 70


def test_empty_answer_scores_none_offline():
    """The real deterministic fallback grades an empty answer as none."""
    catalog = load_catalog()
    role = catalog.role("network_engineer")
    comp = role.competencies[0]
    evaluation, mode = assessor.evaluate_answer(role, comp, "Explain it.", "")
    assert evaluation["level"] == "none"
    assert mode == "deterministic"


def test_not_sure_scores_none_offline():
    """The real deterministic fallback grades "not sure" as none, not aware."""
    catalog = load_catalog()
    role = catalog.role("network_engineer")
    comp = role.competencies[0]
    evaluation, _ = assessor.evaluate_answer(role, comp, "Explain it.", "not sure")
    assert evaluation["level"] == "none"


def test_aggregation_guard_never_defaults_up():
    """A missing or unrecognised level scores none, never the target."""
    scored = [
        {"competency_id": "routing", "level": "none"},
        {"competency_id": "acls"},  # missing level
        {"competency_id": "nat_pat", "level": ""},  # empty
        {"competency_id": "switching_vlans", "level": "???"},  # off-scale
    ]
    attained = aggregate_scores(scored)
    assert attained == {"routing": 0, "acls": 0, "nat_pat": 0, "switching_vlans": 0}

    catalog = load_catalog()
    role = catalog.role("network_engineer")
    result = compute_readiness(role, attained, set(attained))
    assert result.readiness_percent == 0


def test_eval_prompt_states_the_non_answer_rule():
    """The rubric must spell out the hard non-answer rule and show it by example."""
    system = assessor._EVAL_SYSTEM.lower()
    assert "not sure" in system
    assert "none" in system
    assert "never" in system
    # A "not sure" few-shot example must be graded none.
    not_sure = [
        (u, a) for (u, a) in assessor._EVAL_EXAMPLES if "not sure" in u.lower()
    ]
    assert not_sure, "expected a 'not sure' few-shot example"
    assert '"level": "none"' in not_sure[0][1]
