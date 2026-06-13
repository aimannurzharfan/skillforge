"""Deterministic domain core.

Everything that must be authoritative lives here and is computed in code from
data/roles.json: the role profiles, the level scale, score aggregation, gap
computation, and the readiness math. The language model never decides any of it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .config import ROLES_PATH

# Ordered competency scale shared by target levels and assessment results.
LEVEL_ORDER = ["none", "aware", "working", "proficient"]
LEVEL_VALUE = {name: i for i, name in enumerate(LEVEL_ORDER)}
MAX_LEVEL = len(LEVEL_ORDER) - 1

# How many competencies the mock assessment covers, picked by descending weight.
# Kept small so the demo assessment stays short.
DEFAULT_ASSESSMENT_SIZE = 5


def level_to_value(level: str) -> int:
    return LEVEL_VALUE[level]


def value_to_level(value: int) -> str:
    value = max(0, min(MAX_LEVEL, int(round(value))))
    return LEVEL_ORDER[value]


@dataclass(frozen=True)
class Competency:
    id: str
    name: str
    detail: str
    weight: float
    target_level: str

    @property
    def target_value(self) -> int:
        return level_to_value(self.target_level)


@dataclass(frozen=True)
class Role:
    id: str
    name: str
    summary: str
    foundational_tools: list[str]
    competencies: list[Competency]
    builds_on: str | None = None

    def competency(self, competency_id: str) -> Competency | None:
        return next((c for c in self.competencies if c.id == competency_id), None)


@dataclass(frozen=True)
class Topic:
    """Maps a competency to the seed-corpus docs that ground it."""

    competency_id: str
    query: str
    source_docs: list[str]


@dataclass(frozen=True)
class Catalog:
    level_scale: dict[str, int]
    readiness_threshold: str
    roles: dict[str, Role]
    topics: dict[str, Topic]

    def role(self, role_id: str) -> Role:
        if role_id not in self.roles:
            raise KeyError(f"unknown role: {role_id!r}")
        return self.roles[role_id]

    def topic(self, competency_id: str) -> Topic | None:
        return self.topics.get(competency_id)


@lru_cache(maxsize=1)
def load_catalog(path: str | Path = ROLES_PATH) -> Catalog:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))

    roles: dict[str, Role] = {}
    for r in raw["roles"]:
        competencies = [
            Competency(
                id=c["id"],
                name=c["name"],
                detail=c.get("detail", ""),
                weight=float(c["weight"]),
                target_level=c["target_level"],
            )
            for c in r["competencies"]
        ]
        roles[r["id"]] = Role(
            id=r["id"],
            name=r["name"],
            summary=r["summary"],
            foundational_tools=list(r.get("foundational_tools", [])),
            competencies=competencies,
            builds_on=r.get("builds_on"),
        )

    topics = {
        cid: Topic(competency_id=cid, query=t["query"], source_docs=list(t["source_docs"]))
        for cid, t in raw.get("competency_topics", {}).items()
    }

    return Catalog(
        level_scale=dict(raw["level_scale"]),
        readiness_threshold=raw["readiness_threshold"],
        roles=roles,
        topics=topics,
    )


def list_roles(catalog: Catalog | None = None) -> list[dict]:
    """Lightweight role summaries for the role picker."""
    catalog = catalog or load_catalog()
    out = []
    for role in catalog.roles.values():
        out.append(
            {
                "id": role.id,
                "name": role.name,
                "summary": role.summary,
                "builds_on": role.builds_on,
                "competency_count": len(role.competencies),
                "foundational_tools": role.foundational_tools,
            }
        )
    return out


def assessment_competencies(role: Role, size: int = DEFAULT_ASSESSMENT_SIZE) -> list[Competency]:
    """The competencies the assessment will probe: the highest-weighted ones.

    Ties broken by target level then competency id so the selection is stable.
    """
    ranked = sorted(
        role.competencies,
        key=lambda c: (-c.weight, -c.target_value, c.id),
    )
    return ranked[: max(1, size)]


def aggregate_scores(scored_answers: list[dict]) -> dict[str, int]:
    """Aggregate per-answer results into one attained level per competency.

    Each scored answer is ``{"competency_id": str, "level": str}``. When a
    competency is probed more than once the attained value is the mean, rounded.

    Guard: a missing, empty, or unrecognised level is treated as a non-answer and
    scores ``none`` (value 0). It is never defaulted up to the target or to any
    working/proficient level, so an unanswered competency cannot inflate readiness.
    """
    buckets: dict[str, list[int]] = {}
    for item in scored_answers:
        cid = item["competency_id"]
        level = item.get("level")
        if isinstance(level, str) and level.strip().lower() in LEVEL_VALUE:
            value = level_to_value(level.strip().lower())
        else:
            value = 0
        buckets.setdefault(cid, []).append(value)
    return {cid: round(sum(values) / len(values)) for cid, values in buckets.items()}


def competency_coverage(attained_value: int, target_value: int) -> float:
    """Fraction of the target level reached, capped at 1.0."""
    if target_value <= 0:
        return 1.0
    return min(attained_value / target_value, 1.0)


@dataclass
class CompetencyResult:
    competency_id: str
    name: str
    weight: float
    target_level: str
    attained_level: str
    target_value: int
    attained_value: int
    coverage: float
    meets_target: bool
    gap_levels: int
    assessed: bool


@dataclass
class ReadinessResult:
    role_id: str
    role_name: str
    readiness_percent: int
    threshold: str
    competencies: list[CompetencyResult]
    strengths: list[CompetencyResult] = field(default_factory=list)
    gaps: list[CompetencyResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "readiness_percent": self.readiness_percent,
            "threshold": self.threshold,
            "competencies": [vars(c) for c in self.competencies],
            "strengths": [vars(c) for c in self.strengths],
            "gaps": [vars(c) for c in self.gaps],
        }


def compute_readiness(
    role: Role,
    attained: dict[str, int],
    assessed_ids: set[str] | None = None,
    catalog: Catalog | None = None,
) -> ReadinessResult:
    """Weighted coverage of the role's competencies.

    Readiness is computed only over the competencies that were assessed, with
    their weights renormalised to sum to one, so the gauge reflects the answers
    actually given rather than penalising competencies that were never probed.
    """
    catalog = catalog or load_catalog()
    assessed_ids = assessed_ids if assessed_ids is not None else set(attained)

    results: list[CompetencyResult] = []
    for comp in role.competencies:
        assessed = comp.id in assessed_ids
        attained_value = attained.get(comp.id, 0)
        coverage = competency_coverage(attained_value, comp.target_value)
        gap_levels = max(0, comp.target_value - attained_value)
        results.append(
            CompetencyResult(
                competency_id=comp.id,
                name=comp.name,
                weight=comp.weight,
                target_level=comp.target_level,
                attained_level=value_to_level(attained_value),
                target_value=comp.target_value,
                attained_value=attained_value,
                coverage=round(coverage, 4),
                meets_target=attained_value >= comp.target_value,
                gap_levels=gap_levels,
                assessed=assessed,
            )
        )

    assessed_results = [r for r in results if r.assessed]
    weight_total = sum(r.weight for r in assessed_results)
    if weight_total > 0:
        readiness = sum(r.weight * r.coverage for r in assessed_results) / weight_total
    else:
        readiness = 0.0

    strengths = [r for r in assessed_results if r.meets_target]
    gaps = sorted(
        (r for r in assessed_results if not r.meets_target),
        key=lambda r: (-r.weight * (1 - r.coverage), -r.weight),
    )

    return ReadinessResult(
        role_id=role.id,
        role_name=role.name,
        readiness_percent=round(readiness * 100),
        threshold=catalog.readiness_threshold,
        competencies=results,
        strengths=strengths,
        gaps=gaps,
    )
