"""Learning planner: a grounded plan for each gap.

Model-driven and grounded. For every gap, the planner first retrieves passages
from the knowledge base, then asks the model to write a short plan that draws
only on those passages. The citations attached to each plan come from the
retrieval layer (code), not from the model, so every plan is traceable to a
source. On any model failure the planner composes the plan from the passages
deterministically.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from .. import guardrails
from ..domain import Catalog, CompetencyResult, ReadinessResult, load_catalog
from ..foundry_client import ModelUnavailable, chat_json, is_configured
from ..knowledge.interface import KnowledgeBackend, Passage
from ..schemas import SchemaError, validate_plan

MAX_PLANS = 5
PASSAGES_PER_GAP = 3
# Each gap's plan is an independent retrieve-then-write, so they run concurrently
# and the step tracks the slowest plan, not the sum. Cap the fan-out to stay
# inside endpoint rate limits.
_MAX_PLAN_WORKERS = 5

_SYSTEM = (
    "You are an enterprise learning designer building a focused study plan to close one skill gap. "
    "Use only the reference passages provided as your source material; do not add facts beyond them. "
    "Write a one-paragraph summary of how to get from the current level to the target level, then "
    "list two to four concrete learning modules, each with a title and a one-line focus. "
    'Reply with JSON only: {"summary": "...", "modules": [{"title": "...", "focus": "..."}]}.'
)

_EXAMPLE_USER = (
    "Competency: IP addressing and subnetting (VLSM, CIDR)\n"
    "Current level: aware. Target level: proficient.\n"
    "Reference passages:\n"
    "[1] IP Addressing and Subnetting: VLSM lets you size subnets to need; allocate largest to smallest to avoid overlap.\n"
    "[2] IP Addressing and Subnetting: A /24 gives 254 usable hosts; each extra bit halves the host count."
)
_EXAMPLE_ASSISTANT = json.dumps(
    {
        "summary": "Move from recognising subnet notation to designing address plans under constraints by practising VLSM end to end, allocating largest blocks first and verifying no overlaps.",
        "modules": [
            {"title": "CIDR and host math drills", "focus": "Compute usable hosts and ranges for any prefix length quickly."},
            {"title": "VLSM design lab", "focus": "Carve a campus block into right-sized subnets from largest to smallest."},
        ],
    }
)


def build_plans(
    readiness: ReadinessResult,
    backend: KnowledgeBackend,
    catalog: Catalog | None = None,
) -> tuple[list[dict], str]:
    """Return (plans, mode). mode is 'model' if the model wrote any plan."""
    catalog = catalog or load_catalog()
    gaps = readiness.gaps[:MAX_PLANS]

    def build_one(gap: CompetencyResult) -> tuple[dict, str]:
        passages = _retrieve_for(gap, backend, catalog)
        plan_body, mode = _plan_for_gap(gap, passages)
        # Guardrail: keep every citation tied to a passage actually retrieved, so
        # nothing the model might surface can slip in as an invented source.
        citations = guardrails.ground_citations(
            [p.to_dict() for p in passages], [p.doc_id for p in passages]
        )
        plan = {
            "competency_id": gap.competency_id,
            "name": gap.name,
            "attained_level": gap.attained_level,
            "target_level": gap.target_level,
            "summary": plan_body["summary"],
            "modules": plan_body["modules"],
            "citations": citations,
        }
        return plan, mode

    if gaps:
        with ThreadPoolExecutor(max_workers=min(_MAX_PLAN_WORKERS, len(gaps))) as pool:
            built = list(pool.map(build_one, gaps))
    else:
        built = []

    plans = [plan for plan, _ in built]
    used_model = any(mode == "model" for _, mode in built)
    mode = "model" if used_model else ("deterministic" if plans else "none")
    return plans, mode


def _retrieve_for(gap: CompetencyResult, backend: KnowledgeBackend, catalog: Catalog) -> list[Passage]:
    topic = catalog.topic(gap.competency_id)
    if topic is None:
        return backend.retrieve(gap.name, k=PASSAGES_PER_GAP)
    return backend.retrieve(topic.query, k=PASSAGES_PER_GAP, doc_ids=topic.source_docs)


def _plan_for_gap(gap: CompetencyResult, passages: list[Passage]) -> tuple[dict, str]:
    if is_configured() and passages:
        refs = "\n".join(f"[{i + 1}] {p.title}: {p.text}" for i, p in enumerate(passages))
        user = (
            f"Competency: {gap.name}\n"
            f"Current level: {gap.attained_level}. Target level: {gap.target_level}.\n"
            f"Reference passages:\n{refs}"
        )
        try:
            payload = chat_json(
                _SYSTEM, user, example_user=_EXAMPLE_USER, example_assistant=_EXAMPLE_ASSISTANT
            )
            return validate_plan(payload), "model"
        except (ModelUnavailable, SchemaError):
            pass
    return _fallback_plan(gap, passages), "deterministic"


def _fallback_plan(gap: CompetencyResult, passages: list[Passage]) -> dict:
    summary = (
        f"Raise {gap.name.lower()} from {gap.attained_level} to {gap.target_level} by studying the "
        f"cited material and practising it hands on."
    )
    modules = []
    for p in passages:
        first_sentence = p.text.split(". ")[0].strip().rstrip(".")
        modules.append(
            {
                "title": f"Study: {p.title}",
                "focus": (first_sentence[:160] + ".") if first_sentence else p.title,
            }
        )
    if not modules:
        modules = [{"title": f"Build {gap.name}", "focus": f"Reach {gap.target_level} level through guided practice."}]
    return {"summary": summary, "modules": modules}
