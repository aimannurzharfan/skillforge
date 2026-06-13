"""Role profiler: loads the target role's competency profile.

Purely deterministic. This is the semantic business model: it reads the curated
profile from data/roles.json and decides which competencies the assessment will
probe. No model call.
"""

from __future__ import annotations

from ..domain import Catalog, Role, assessment_competencies, load_catalog


def build_profile(role_id: str, catalog: Catalog | None = None) -> dict:
    catalog = catalog or load_catalog()
    role: Role = catalog.role(role_id)
    probed = assessment_competencies(role)
    probed_ids = {c.id for c in probed}

    return {
        "role": {
            "id": role.id,
            "name": role.name,
            "summary": role.summary,
            "builds_on": role.builds_on,
            "foundational_tools": role.foundational_tools,
        },
        "competencies": [
            {
                "id": c.id,
                "name": c.name,
                "detail": c.detail,
                "weight": c.weight,
                "target_level": c.target_level,
                "probed": c.id in probed_ids,
            }
            for c in role.competencies
        ],
        "assessment_competencies": [
            {"id": c.id, "name": c.name, "detail": c.detail, "target_level": c.target_level}
            for c in probed
        ],
    }
