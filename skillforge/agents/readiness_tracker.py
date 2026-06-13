"""Readiness tracker: the role-readiness scorecard.

Purely deterministic. It runs the readiness math from domain.compute_readiness
and turns the result into strengths, gaps, and concrete next steps. No model call.
The readiness percent it returns is the hero number shown on the gauge.
"""

from __future__ import annotations

from ..domain import ReadinessResult, Role, compute_readiness


def track(role: Role, attained: dict[str, int], assessed_ids: set[str]) -> ReadinessResult:
    return compute_readiness(role, attained, assessed_ids)


def next_steps(readiness: ReadinessResult, limit: int = 3) -> list[dict]:
    """The highest-leverage moves: the weightiest unmet competencies first."""
    steps = []
    for gap in readiness.gaps[:limit]:
        steps.append(
            {
                "competency_id": gap.competency_id,
                "name": gap.name,
                "from_level": gap.attained_level,
                "to_level": gap.target_level,
                "weight": gap.weight,
                "action": f"Raise {gap.name} from {gap.attained_level} to {gap.target_level}.",
            }
        )
    return steps
