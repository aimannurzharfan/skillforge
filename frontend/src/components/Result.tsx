import type { CompetencyResult, ResultData } from "../types";
import AgentTimeline from "./AgentTimeline";
import ReadinessGauge from "./ReadinessGauge";
import { Label, LevelMeter, LevelTag } from "./ui";
import { LEVEL_INDEX } from "./levels";

function CompetencyRow({ c }: { c: CompetencyResult }) {
  return (
    <li className="flex items-center gap-4 py-3">
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-mist-200">{c.name}</p>
        <p className="mt-0.5 font-mono text-[0.7rem] text-mist-400 tnum">
          weight {Math.round(c.weight * 100)}% &middot; <LevelTag level={c.attained_level} /> to
          target {c.target_level}
        </p>
      </div>
      <LevelMeter attained={LEVEL_INDEX[c.attained_level] ?? 0} target={LEVEL_INDEX[c.target_level] ?? 0} />
    </li>
  );
}

export default function Result({ data, onRestart }: { data: ResultData; onRestart: () => void }) {
  return (
    <div className="space-y-7">
      {/* Hero: the readiness gauge leads, the verdict reads beside it. */}
      <section className="panel rounded-3xl p-6 sm:p-8" aria-labelledby="readiness-h">
        <div className="grid items-center gap-8 md:grid-cols-[280px_1fr]">
          <ReadinessGauge percent={data.readiness_percent} threshold={data.threshold} />
          <div>
            <Label className="text-ember-400">Readiness for {data.role_name}</Label>
            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[0.7rem] text-mist-400 tnum">
              <span title="Measured wall-clock time from submit to readiness and plan">
                Assessed and planned in{" "}
                <span className="text-mist-200">{data.elapsed_seconds.toFixed(1)}s</span>
              </span>
              <span aria-hidden="true" className="h-1 w-1 rounded-full bg-ink-600" />
              <span title="Safety gates passed this run: schema, non-answer rule, grounded citations, taxonomy">
                Guardrails{" "}
                <span className={data.guardrails.passed === data.guardrails.total ? "text-emerald-400" : "text-amber-300"}>
                  {data.guardrails.passed}/{data.guardrails.total}
                </span>
              </span>
            </div>
            <p id="readiness-h" className="mt-3 text-xl leading-relaxed text-mist-100 text-pretty">
              {data.narrative}
            </p>
            {data.next_steps.length > 0 && (
              <div className="mt-5">
                <p className="text-sm font-semibold text-mist-200">Highest-leverage next steps</p>
                <ul className="mt-2 space-y-1.5">
                  {data.next_steps.map((s) => (
                    <li key={s.competency_id} className="flex gap-2 text-sm text-mist-300">
                      <span aria-hidden="true" className="text-ember-500">
                        &rarr;
                      </span>
                      {s.action}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {!data.model_configured && (
              <p className="mt-5 text-xs leading-relaxed text-mist-400">
                The model endpoint was not configured, so questions and narratives used the
                deterministic fallback. The readiness score is computed in code either way.
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Where you stand */}
      <section aria-labelledby="standing-h">
        <h2 id="standing-h" className="text-sm font-semibold text-mist-200">
          Where you stand
        </h2>
        <div className="mt-3 grid grid-cols-1 gap-5 lg:grid-cols-2">
          <div className="panel rounded-2xl p-5">
            <p className="label mb-1 text-emerald-400">Meets target &middot; {data.strengths.length}</p>
            {data.strengths.length === 0 ? (
              <p className="py-3 text-sm text-mist-400">
                No competency has reached its target yet. The plan below is where to start.
              </p>
            ) : (
              <ul className="divide-y divide-ink-700">
                {data.strengths.map((c) => (
                  <CompetencyRow key={c.competency_id} c={c} />
                ))}
              </ul>
            )}
          </div>

          <div className="panel rounded-2xl p-5">
            <p className="label mb-1 text-ember-400">Below target &middot; {data.gaps.length}</p>
            {data.gaps.length === 0 ? (
              <p className="py-3 text-sm text-mist-400">
                No gaps in the assessed competencies. A strong result.
              </p>
            ) : (
              <ul className="divide-y divide-ink-700">
                {data.gaps.map((c) => (
                  <CompetencyRow key={c.competency_id} c={c} />
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>

      {/* Grounded learning plan */}
      {data.learning_plans.length > 0 && (
        <section aria-labelledby="plan-h">
          <h2 id="plan-h" className="text-sm font-semibold text-mist-200">
            Grounded learning plan
          </h2>
          <div className="mt-3 grid grid-cols-1 gap-5 md:grid-cols-2">
            {data.learning_plans.map((plan) => (
              <article key={plan.competency_id} className="panel flex flex-col rounded-2xl p-5">
                <div className="flex items-baseline justify-between gap-3">
                  <h3 className="text-base font-semibold text-mist-100">{plan.name}</h3>
                  <span className="shrink-0 font-mono text-[0.7rem] text-mist-400">
                    {plan.attained_level} to {plan.target_level}
                  </span>
                </div>
                <p className="mt-2 text-sm text-mist-300">{plan.summary}</p>
                <ol className="mt-3 divide-y divide-ink-700/70 border-y border-ink-700/70">
                  {plan.modules.map((m, i) => (
                    <li key={i} className="flex gap-3 py-2.5">
                      <span className="font-mono text-xs text-ember-400 tnum">{i + 1}</span>
                      <div>
                        <p className="text-sm font-medium text-mist-200">{m.title}</p>
                        <p className="text-sm text-mist-400">{m.focus}</p>
                      </div>
                    </li>
                  ))}
                </ol>
                {plan.citations.length > 0 && (
                  <div className="mt-3">
                    <p className="label mb-1.5 text-steel-400">Sources</p>
                    <ul className="space-y-1">
                      {plan.citations.map((c, i) => (
                        <li key={i} className="font-mono text-[0.7rem] text-mist-400">
                          <span className="text-steel-400">[{c.source}]</span> {c.citation}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      {/* Per-answer scoring */}
      <details className="panel rounded-2xl p-5">
        <summary className="cursor-pointer text-sm font-semibold text-mist-200">
          Per-answer scoring ({data.evaluations.length})
        </summary>
        <ul className="mt-4 divide-y divide-ink-700">
          {data.evaluations.map((e) => (
            <li key={e.competency_id} className="py-3">
              <div className="flex items-center gap-2">
                <span className="label text-ember-400">{e.competency_name}</span>
                <LevelTag level={e.level} />
                <span className="ml-auto font-mono text-xs text-mist-400 tnum">{e.score} / 100</span>
              </div>
              <p className="mt-1 text-sm text-mist-400">{e.rationale}</p>
            </li>
          ))}
        </ul>
      </details>

      <AgentTimeline steps={data.steps} title="Pipeline: scoring, gaps and plan" />

      <div className="flex justify-center pb-4">
        <button
          type="button"
          onClick={onRestart}
          className="rounded-xl border border-ink-600 px-5 py-2.5 font-semibold text-mist-200 transition-colors hover:border-ember-500/60 hover:text-mist-100"
        >
          Assess another role
        </button>
      </div>
    </div>
  );
}
