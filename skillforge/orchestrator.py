"""Orchestrator: runs the multi-agent pipeline and logs every step.

The flow has two phases. ``start_assessment`` profiles the role and generates the
questions. ``complete_assessment`` evaluates the answers, computes readiness and
gaps in code, writes the gap narrative, and builds the grounded learning plans.
Each agent invocation is recorded as a step with its agent name and whether it
ran model-driven or deterministic, which the UI surfaces so the multi-agent work
is visible.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from .agents import (
    assessor,
    gap_analyzer,
    learning_planner,
    readiness_tracker,
    role_profiler,
)
from .domain import Catalog, aggregate_scores, load_catalog
from .foundry_client import is_configured
from .knowledge.interface import KnowledgeBackend, get_backend
from .sanitize import sanitize_identifier, sanitize_user_text

logger = logging.getLogger("skillforge.orchestrator")

# The per-answer evaluations are independent model calls, so they run
# concurrently. Cap the fan-out to stay well inside endpoint rate limits.
_MAX_EVAL_WORKERS = 5


@dataclass
class StepLog:
    steps: list[dict] = field(default_factory=list)

    def record(self, agent: str, action: str, mode: str, detail: str, started: float) -> None:
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        entry = {
            "agent": agent,
            "action": action,
            "mode": mode,  # "deterministic", "model", or "code"
            "detail": detail,
            "elapsed_ms": elapsed_ms,
        }
        self.steps.append(entry)
        logger.info("step agent=%s action=%s mode=%s detail=%s (%dms)", agent, action, mode, detail, elapsed_ms)


class Orchestrator:
    def __init__(self, catalog: Catalog | None = None, backend: KnowledgeBackend | None = None) -> None:
        self.catalog = catalog or load_catalog()
        self.backend = backend or get_backend()

    # Phase 1: role profile plus mock-assessment questions.
    def start_assessment(self, role_id: str) -> dict:
        role_id = sanitize_identifier(role_id)
        log = StepLog()

        started = time.perf_counter()
        profile = role_profiler.build_profile(role_id, self.catalog)
        role = self.catalog.role(role_id)
        log.record(
            "role_profiler", "Load competency profile", "deterministic",
            f"{role.name}: {len(role.competencies)} competencies", started,
        )

        probed = [role.competency(c["id"]) for c in profile["assessment_competencies"]]
        started = time.perf_counter()
        questions, mode = assessor.generate_questions(role, probed)
        log.record(
            "assessor", "Generate assessment questions", mode,
            f"{len(questions)} questions for the top competencies", started,
        )

        names = {c.id: c.name for c in role.competencies}
        return {
            "role": profile["role"],
            "competencies": profile["competencies"],
            "questions": [
                {
                    "competency_id": q["competency_id"],
                    "competency_name": names.get(q["competency_id"], q["competency_id"]),
                    "question": q["question"],
                }
                for q in questions
            ],
            "knowledge_backend": self.backend.name,
            "steps": log.steps,
        }

    # Phase 2: evaluate answers and produce the full readiness result.
    def complete_assessment(self, role_id: str, answers: list[dict]) -> dict:
        role_id = sanitize_identifier(role_id)
        role = self.catalog.role(role_id)
        log = StepLog()

        # Assessor: grade each free-text answer. The evaluations are independent
        # model calls, so they run concurrently; results are reassembled in the
        # original answer order so aggregation stays deterministic.
        started = time.perf_counter()
        gradable = []
        for ans in answers:
            cid = sanitize_identifier(ans.get("competency_id", ""))
            competency = role.competency(cid)
            if competency is None:
                continue
            gradable.append((cid, competency, ans.get("question", ""), ans.get("answer", "")))

        def grade(item):
            cid, competency, question, answer_text = item
            return cid, competency, question, assessor.evaluate_answer(
                role, competency, question, answer_text
            )

        if gradable:
            with ThreadPoolExecutor(max_workers=min(_MAX_EVAL_WORKERS, len(gradable))) as pool:
                graded = list(pool.map(grade, gradable))
        else:
            graded = []

        scored: list[dict] = []
        evaluations: list[dict] = []
        used_model = False
        for cid, competency, question, (evaluation, mode) in graded:
            used_model = used_model or mode == "model"
            scored.append({"competency_id": cid, "level": evaluation["level"]})
            evaluations.append(
                {
                    "competency_id": cid,
                    "competency_name": competency.name,
                    "question": sanitize_user_text(question, max_len=600),
                    "level": evaluation["level"],
                    "score": evaluation["score"],
                    "rationale": evaluation["rationale"],
                }
            )
        log.record(
            "assessor", "Evaluate answers", "model" if used_model else "deterministic",
            f"graded {len(scored)} answers", started,
        )

        # Code: aggregate to one attained level per competency.
        started = time.perf_counter()
        attained = aggregate_scores(scored)
        assessed_ids = set(attained)
        log.record(
            "orchestrator", "Aggregate per-competency scores", "code",
            f"{len(attained)} competencies scored", started,
        )

        # Readiness tracker: the deterministic readiness math.
        started = time.perf_counter()
        readiness = readiness_tracker.track(role, attained, assessed_ids)
        steps_to_take = readiness_tracker.next_steps(readiness)
        log.record(
            "readiness_tracker", "Compute role readiness", "deterministic",
            f"{readiness.readiness_percent}% ready, {len(readiness.gaps)} gaps", started,
        )

        # Gap analyzer: code already has the gaps; the model writes the story.
        started = time.perf_counter()
        narrative, mode = gap_analyzer.write_narrative(role, readiness)
        log.record("gap_analyzer", "Write gap narrative", mode, "narrative composed", started)

        # Learning planner: grounded plan per gap, with citations.
        started = time.perf_counter()
        plans, plan_mode = learning_planner.build_plans(readiness, self.backend, self.catalog)
        total_citations = sum(len(p["citations"]) for p in plans)
        log.record(
            "learning_planner", "Build grounded learning plan", plan_mode,
            f"{len(plans)} plans, {total_citations} citations from {self.backend.name}", started,
        )

        result = readiness.to_dict()
        result.update(
            {
                "evaluations": evaluations,
                "narrative": narrative,
                "next_steps": steps_to_take,
                "learning_plans": plans,
                "knowledge_backend": self.backend.name,
                "model_configured": is_configured(),
                "steps": log.steps,
            }
        )
        return result
