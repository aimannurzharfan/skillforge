import type { CompetencyResult, ResultData } from "../types";
import AgentTimeline from "./AgentTimeline";
import ReadinessGauge from "./ReadinessGauge";
import { Kicker, LevelMeter, LevelTag } from "./ui";
import { LEVEL_INDEX } from "./levels";

function CompetencyRow({ c }: { c: CompetencyResult }) {
  return (
    <li className="flex items-center gap-4 py-3">
      <div className="min-w-0 flex-1">
        <p className="truncate font-display text-sm font-medium text-mist-200">{c.name}</p>
        <p className="font-mono text-[0.65rem] text-mist-400">
          weight {Math.round(c.weight * 100)}% · <LevelTag level={c.attained_level} /> → target {c.target_level}
        </p>
      </div>
      <LevelMeter attained={LEVEL_INDEX[c.attained_level] ?? 0} target={LEVEL_INDEX[c.target_level] ?? 0} />
    </li>
  );
}

export default function Result({ data, onRestart }: { data: ResultData; onRestart: () => void }) {
  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="panel grid grid-cols-1 items-center gap-6 rounded-3xl p-6 md:grid-cols-[260px_1fr]">
        <ReadinessGauge percent={data.readiness_percent} threshold={data.threshold} />
        <div>
          <Kicker>Step 3 — readiness for {data.role_name}</Kicker>
          <p className="mt-3 font-display text-xl leading-relaxed text-mist-200">{data.narrative}</p>
          {data.next_steps.length > 0 && (
            <div className="mt-4">
              <p className="kicker text-mist-400">Highest-leverage next steps</p>
              <ul className="mt-2 space-y-1">
                {data.next_steps.map((s) => (
                  <li key={s.competency_id} className="text-sm text-mist-200">
                    <span className="text-ember-400">▸</span> {s.action}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {!data.model_configured && (
            <p className="mt-4 rounded-lg border border-ink-600 bg-white/5 px-3 py-2 font-mono text-[0.65rem] text-mist-400">
              Model endpoint not configured — questions and narratives used the deterministic fallback.
            </p>
          )}
        </div>
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Strengths */}
        <section className="panel rounded-2xl p-5" aria-labelledby="strengths-h">
          <h2 id="strengths-h" className="kicker mb-1 text-emerald-400">
            Strengths · meets target ({data.strengths.length})
          </h2>
          {data.strengths.length === 0 ? (
            <p className="py-3 text-sm text-mist-400">No competencies met target yet — every step counts.</p>
          ) : (
            <ul className="divide-y divide-ink-700">
              {data.strengths.map((c) => (
                <CompetencyRow key={c.competency_id} c={c} />
              ))}
            </ul>
          )}
        </section>

        {/* Gaps */}
        <section className="panel rounded-2xl p-5" aria-labelledby="gaps-h">
          <h2 id="gaps-h" className="kicker mb-1 text-ember-400">
            Gaps · below target ({data.gaps.length})
          </h2>
          {data.gaps.length === 0 ? (
            <p className="py-3 text-sm text-mist-400">No gaps in the assessed competencies. Strong result.</p>
          ) : (
            <ul className="divide-y divide-ink-700">
              {data.gaps.map((c) => (
                <CompetencyRow key={c.competency_id} c={c} />
              ))}
            </ul>
          )}
        </section>
      </div>

      {/* Learning plan */}
      {data.learning_plans.length > 0 && (
        <section aria-labelledby="plan-h">
          <h2 id="plan-h" className="kicker text-ember-400">
            Grounded learning plan
          </h2>
          <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
            {data.learning_plans.map((plan) => (
              <article key={plan.competency_id} className="panel rounded-2xl p-5">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="font-display text-lg font-semibold text-mist-200">{plan.name}</h3>
                  <span className="font-mono text-[0.65rem] text-mist-400">
                    {plan.attained_level} → {plan.target_level}
                  </span>
                </div>
                <p className="mt-2 text-sm text-mist-400">{plan.summary}</p>
                <ul className="mt-3 space-y-2">
                  {plan.modules.map((m, i) => (
                    <li key={i} className="rounded-lg border border-ink-700 bg-ink-900/40 p-3">
                      <p className="font-display text-sm font-medium text-mist-200">{m.title}</p>
                      <p className="text-sm text-mist-400">{m.focus}</p>
                    </li>
                  ))}
                </ul>
                {plan.citations.length > 0 && (
                  <div className="mt-3 border-t border-ink-700 pt-3">
                    <p className="kicker mb-1 text-steel-400">Cited sources</p>
                    <ul className="space-y-1">
                      {plan.citations.map((c, i) => (
                        <li key={i} className="font-mono text-[0.68rem] text-mist-400">
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

      {/* Per-answer evaluations */}
      <details className="panel rounded-2xl p-5">
        <summary className="cursor-pointer font-display text-sm font-semibold text-mist-200">
          Per-answer scoring ({data.evaluations.length})
        </summary>
        <ul className="mt-4 space-y-3">
          {data.evaluations.map((e) => (
            <li key={e.competency_id} className="border-l-2 border-ink-600 pl-3">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs uppercase tracking-wider text-ember-400">{e.competency_name}</span>
                <LevelTag level={e.level} />
                <span className="ml-auto font-mono text-xs text-mist-400">{e.score}/100</span>
              </div>
              <p className="text-sm text-mist-400">{e.rationale}</p>
            </li>
          ))}
        </ul>
      </details>

      <AgentTimeline steps={data.steps} title="Agents · scoring, gaps & plan" />

      <div className="flex justify-center pb-4">
        <button
          type="button"
          onClick={onRestart}
          className="rounded-xl border border-ink-600 px-6 py-3 font-display font-semibold text-mist-200 transition-colors hover:border-ember-500/60"
        >
          Assess another role
        </button>
      </div>
    </div>
  );
}
