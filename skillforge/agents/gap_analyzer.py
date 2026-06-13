"""Gap analyzer: a hybrid agent.

The gaps themselves are computed in code (in domain.compute_readiness) from the
target levels and the assessed levels. This agent only asks the model to turn
that deterministic gap list into a short, readable narrative for the learner.
On any model failure it composes the narrative deterministically.
"""

from __future__ import annotations

from ..domain import ReadinessResult, Role
from ..foundry_client import ModelUnavailable, chat_json, is_configured
from ..schemas import SchemaError, validate_narrative

_SYSTEM = (
    "You are a learning advisor summarising a role-readiness assessment for an employee. "
    "You are given the role, the readiness percent, and the competency gaps already computed "
    "by the system. Write two or three plain sentences: where they stand, the most important "
    "gaps to close, and an encouraging next focus. Do not invent scores or competencies. "
    'Reply with JSON only: {"narrative": "..."}.'
)

_EXAMPLE_USER = (
    "Role: Network Engineer\nReadiness: 64%\n"
    "Strengths: Routing (proficient), Switching and VLANs (working)\n"
    "Gaps: IP addressing and subnetting (working now, target proficient), ACLs (aware now, target working)"
)
_EXAMPLE_ASSISTANT = (
    '{"narrative": "You are about two thirds of the way to Network Engineer readiness, with solid '
    "routing and switching. The biggest lift is getting subnetting to a proficient level, followed by "
    'tightening up ACLs. Focus there next and the role comes within reach."}'
)


def write_narrative(role: Role, readiness: ReadinessResult) -> tuple[str, str]:
    """Return (narrative, mode)."""
    if is_configured():
        try:
            payload = chat_json(
                _SYSTEM, _format_user(role, readiness),
                example_user=_EXAMPLE_USER, example_assistant=_EXAMPLE_ASSISTANT,
            )
            return validate_narrative(payload), "model"
        except (ModelUnavailable, SchemaError):
            pass
    return _fallback_narrative(role, readiness), "deterministic"


def _format_user(role: Role, readiness: ReadinessResult) -> str:
    strengths = ", ".join(f"{s.name} ({s.attained_level})" for s in readiness.strengths) or "none yet"
    gaps = (
        ", ".join(
            f"{g.name} ({g.attained_level} now, target {g.target_level})" for g in readiness.gaps
        )
        or "none"
    )
    return (
        f"Role: {role.name}\nReadiness: {readiness.readiness_percent}%\n"
        f"Strengths: {strengths}\nGaps: {gaps}"
    )


def _fallback_narrative(role: Role, readiness: ReadinessResult) -> str:
    if not readiness.gaps:
        return (
            f"You are at {readiness.readiness_percent}% readiness for {role.name} and meet the target "
            f"level on every competency assessed. Keep these skills current and consider the next role."
        )
    top = readiness.gaps[0]
    others = [g.name for g in readiness.gaps[1:3]]
    tail = f" Then look at {', '.join(others)}." if others else ""
    return (
        f"You are at {readiness.readiness_percent}% readiness for {role.name}. The most important gap "
        f"to close is {top.name}, currently {top.attained_level} against a target of {top.target_level}.{tail}"
    )
