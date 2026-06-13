import type { Step } from "../types";
import { ModeBadge } from "./ui";

const AGENT_LABEL: Record<string, string> = {
  role_profiler: "Role Profiler",
  assessor: "Assessor",
  orchestrator: "Orchestrator",
  readiness_tracker: "Readiness Tracker",
  gap_analyzer: "Gap Analyzer",
  learning_planner: "Learning Planner",
};

/** Makes the multi-agent work visible: each orchestrated step, in order. */
export default function AgentTimeline({ steps, title }: { steps: Step[]; title: string }) {
  return (
    <section className="panel rounded-2xl p-5" aria-label={title}>
      <h2 className="kicker mb-4 text-steel-400">{title}</h2>
      <ol className="space-y-3">
        {steps.map((s, i) => (
          <li key={i} className="flex items-start gap-3">
            <span
              className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-ink-700 font-mono text-xs text-mist-400"
              aria-hidden="true"
            >
              {i + 1}
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                <span className="font-display text-sm font-semibold text-mist-200">
                  {AGENT_LABEL[s.agent] ?? s.agent}
                </span>
                <ModeBadge mode={s.mode} />
                <span className="ml-auto font-mono text-[0.65rem] text-mist-400">{s.elapsed_ms} ms</span>
              </div>
              <p className="text-sm text-mist-400">
                {s.action} — {s.detail}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
