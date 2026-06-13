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

/** Makes the multi-agent work legible: each orchestrated step, in order. */
export default function AgentTimeline({ steps, title }: { steps: Step[]; title: string }) {
  return (
    <section className="panel rounded-2xl p-5" aria-label={title}>
      <h2 className="label mb-4 text-mist-400">{title}</h2>
      <ol className="space-y-3.5">
        {steps.map((s, i) => (
          <li key={i} className="relative pl-4">
            <span
              aria-hidden="true"
              className="absolute left-0 top-1.5 h-1.5 w-1.5 rounded-full bg-ink-600"
            />
            <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
              <span className="text-sm font-semibold text-mist-200">
                {AGENT_LABEL[s.agent] ?? s.agent}
              </span>
              <ModeBadge mode={s.mode} />
              <span className="ml-auto font-mono text-[0.65rem] text-mist-400 tnum">
                {s.elapsed_ms} ms
              </span>
            </div>
            <p className="mt-0.5 text-[0.8rem] leading-snug text-mist-400">{s.detail}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
