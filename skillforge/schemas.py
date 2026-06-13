"""Tight validators for every model output.

The model only ever returns language wrapped in a small JSON object. Each agent
validates the response here before trusting it; on any failure the agent falls
back to deterministic text. Validators are intentionally dependency-free and
strict about types so a malformed or injected payload is rejected, not used.
"""

from __future__ import annotations

from .domain import LEVEL_ORDER


class SchemaError(ValueError):
    """Raised when a model payload does not match the expected shape."""


def _require_mapping(value: object, where: str) -> dict:
    if not isinstance(value, dict):
        raise SchemaError(f"{where}: expected an object, got {type(value).__name__}")
    return value


def _require_str(value: object, where: str, *, min_len: int = 1, max_len: int = 4000) -> str:
    if not isinstance(value, str):
        raise SchemaError(f"{where}: expected a string")
    text = value.strip()
    if len(text) < min_len:
        raise SchemaError(f"{where}: string too short")
    if len(text) > max_len:
        raise SchemaError(f"{where}: string too long ({len(text)} > {max_len})")
    return text


def validate_questions(payload: object, expected_ids: list[str]) -> list[dict]:
    """Assessment questions: one per expected competency id, in any order."""
    data = _require_mapping(payload, "questions")
    items = data.get("questions")
    if not isinstance(items, list) or not items:
        raise SchemaError("questions: 'questions' must be a non-empty list")

    expected = set(expected_ids)
    seen: dict[str, str] = {}
    for i, item in enumerate(items):
        obj = _require_mapping(item, f"questions[{i}]")
        cid = _require_str(obj.get("competency_id"), f"questions[{i}].competency_id", max_len=120)
        if cid not in expected:
            raise SchemaError(f"questions[{i}]: unexpected competency_id {cid!r}")
        question = _require_str(obj.get("question"), f"questions[{i}].question", max_len=600)
        seen[cid] = question

    missing = expected - set(seen)
    if missing:
        raise SchemaError(f"questions: missing competencies {sorted(missing)}")
    return [{"competency_id": cid, "question": seen[cid]} for cid in expected_ids]


def validate_evaluation(payload: object) -> dict:
    """A single free-text answer evaluation."""
    data = _require_mapping(payload, "evaluation")
    level = data.get("level")
    if level not in LEVEL_ORDER:
        raise SchemaError(f"evaluation.level must be one of {LEVEL_ORDER}, got {level!r}")
    score = data.get("score")
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise SchemaError("evaluation.score must be a number")
    score = max(0, min(100, int(round(score))))
    rationale = _require_str(data.get("rationale"), "evaluation.rationale", max_len=800)
    return {"level": level, "score": score, "rationale": rationale}


def validate_narrative(payload: object) -> str:
    data = _require_mapping(payload, "narrative")
    return _require_str(data.get("narrative"), "narrative.narrative", max_len=1500)


def validate_plan(payload: object) -> dict:
    """A learning plan for one gap: a rationale plus a few modules.

    Citations are attached by the planner from the retrieval layer, not taken
    from the model, so they are not validated here.
    """
    data = _require_mapping(payload, "plan")
    summary = _require_str(data.get("summary"), "plan.summary", max_len=1200)
    modules = data.get("modules")
    if not isinstance(modules, list) or not modules:
        raise SchemaError("plan.modules must be a non-empty list")
    if len(modules) > 6:
        modules = modules[:6]
    clean_modules = []
    for i, mod in enumerate(modules):
        obj = _require_mapping(mod, f"plan.modules[{i}]")
        clean_modules.append(
            {
                "title": _require_str(obj.get("title"), f"plan.modules[{i}].title", max_len=200),
                "focus": _require_str(obj.get("focus"), f"plan.modules[{i}].focus", max_len=600),
            }
        )
    return {"summary": summary, "modules": clean_modules}
