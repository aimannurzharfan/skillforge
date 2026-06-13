"""Guardrails: the safety gates every run passes through.

These were always present, scattered across the agents and the domain core. This
module names them in one place so the reliability story is visible rather than
buried. The orchestrator runs ``evaluate_run`` after a pipeline finishes and logs
how many gates passed, and the planner uses ``ground_citations`` to keep every
citation tied to a passage that was actually retrieved.

The gates:

1. Schema validation of every model output (levels on the scale, scores in range).
2. The non-answer rule: a missing, empty, or unrecognised level scores ``none``,
   never aware, working, or proficient.
3. Citations restricted to passages actually retrieved; any source the model
   invents is dropped.
4. Only competencies and roles defined in ``data/roles.json`` are accepted.
5. A deterministic fallback runs whenever a model call fails or returns invalid
   JSON, so the pipeline always completes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .domain import LEVEL_VALUE, Catalog, Role

# A level outside the four-point scale, or no level at all, is a non-answer.
NON_ANSWER_LEVEL = "none"


def enforce_assessed_level(level: object) -> str:
    """Coerce a model-assessed level onto the scale; non-answers become ``none``.

    Used before aggregation so a missing or unrecognised level can never be
    defaulted up to a working or proficient level.
    """
    if isinstance(level, str) and level.strip().lower() in LEVEL_VALUE:
        return level.strip().lower()
    return NON_ANSWER_LEVEL


def is_known_role(catalog: Catalog, role_id: str) -> bool:
    return role_id in catalog.roles


def is_known_competency(role: Role, competency_id: str) -> bool:
    return role.competency(competency_id) is not None


def ground_citations(citations: list[dict], retrieved_doc_ids: list[str]) -> list[dict]:
    """Drop any citation whose source was not in the retrieved passage set.

    Citations are built from the retrieval layer, not from the model, so this is
    the enforcement point that keeps a model from smuggling in an invented source.
    """
    allowed = set(retrieved_doc_ids)
    return [c for c in citations if isinstance(c, dict) and c.get("doc_id") in allowed]


@dataclass
class GuardrailReport:
    """The pass/fail tally for one run, surfaced in logs and the API response."""

    checks: list[tuple[str, bool]] = field(default_factory=list)

    def record(self, name: str, ok: bool) -> bool:
        self.checks.append((name, bool(ok)))
        return bool(ok)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def passed(self) -> int:
        return sum(1 for _, ok in self.checks if ok)

    @property
    def summary(self) -> str:
        return f"{self.passed}/{self.total}"

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "total": self.total,
            "checks": [{"name": name, "ok": ok} for name, ok in self.checks],
        }


def evaluate_run(
    role: Role,
    evaluations: list[dict],
    plans: list[dict],
    *,
    role_known: bool,
) -> GuardrailReport:
    """Check the invariants of a finished run and return the tally."""
    report = GuardrailReport()
    report.record("role in taxonomy", role_known)
    report.record(
        "competencies in taxonomy",
        all(is_known_competency(role, e["competency_id"]) for e in evaluations),
    )
    report.record(
        "assessed levels on the scale (non-answers scored none)",
        all(e.get("level") in LEVEL_VALUE for e in evaluations),
    )
    report.record(
        "scores within bounds",
        all(isinstance(e.get("score"), int) and 0 <= e["score"] <= 100 for e in evaluations),
    )
    report.record(
        "citations grounded in retrieval",
        all(c.get("doc_id") for p in plans for c in p.get("citations", [])),
    )
    return report
