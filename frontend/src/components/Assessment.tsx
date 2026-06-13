import { useState } from "react";
import type { AssessmentStart } from "../types";
import { groundingLabel } from "../types";
import AgentTimeline from "./AgentTimeline";

interface Props {
  start: AssessmentStart;
  submitting: boolean;
  onSubmit: (answers: { competency_id: string; question: string; answer: string }[]) => void;
  onBack: () => void;
}

export default function Assessment({ start, submitting, onSubmit, onBack }: Props) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const answeredCount = start.questions.filter(
    (q) => (answers[q.competency_id] ?? "").trim().length > 0,
  ).length;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = start.questions.map((q) => ({
      competency_id: q.competency_id,
      question: q.question,
      answer: answers[q.competency_id] ?? "",
    }));
    onSubmit(payload);
  };

  const grounding = groundingLabel(start.knowledge_backend);

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_300px]">
      <form onSubmit={handleSubmit} aria-labelledby="assess-heading">
        <h1 id="assess-heading" className="text-2xl font-bold tracking-tight text-mist-100">
          {start.role.name}
        </h1>
        <p className="mt-2 max-w-2xl text-[0.95rem] leading-relaxed text-mist-300">
          Answer in your own words. There is no timer and partial answers still count. The assessor
          grades each on the none, aware, working, proficient scale.
        </p>

        <ol className="mt-7 space-y-4">
          {start.questions.map((q, i) => (
            <li key={q.competency_id} className="panel rounded-2xl p-5">
              <div className="flex items-center justify-between gap-3">
                <span className="label text-ember-400">{q.competency_name}</span>
                <span className="font-mono text-xs text-mist-400 tnum">
                  {i + 1} / {start.questions.length}
                </span>
              </div>
              <label
                htmlFor={`q-${q.competency_id}`}
                className="mt-3 block text-[1.05rem] font-medium leading-snug text-mist-100"
              >
                {q.question}
              </label>
              <textarea
                id={`q-${q.competency_id}`}
                value={answers[q.competency_id] ?? ""}
                onChange={(e) => setAnswers((a) => ({ ...a, [q.competency_id]: e.target.value }))}
                rows={3}
                maxLength={4000}
                placeholder="Type your answer"
                className="mt-3 w-full resize-y rounded-xl border border-ink-600 bg-ink-900/70 p-3 text-mist-100 placeholder:text-mist-400 focus:border-amber-300 focus:outline-none"
              />
            </li>
          ))}
        </ol>

        <div className="mt-6 flex flex-wrap items-center gap-4">
          <button
            type="submit"
            disabled={submitting || answeredCount === 0}
            className="rounded-xl bg-ember-500 px-5 py-2.5 font-semibold text-ink-950 transition-colors hover:bg-ember-400 disabled:cursor-not-allowed disabled:bg-ink-700 disabled:text-mist-400"
          >
            {submitting ? "Scoring with the agents..." : "Score my readiness"}
          </button>
          <button
            type="button"
            onClick={onBack}
            disabled={submitting}
            className="text-sm font-medium text-mist-400 transition-colors hover:text-mist-200"
          >
            Change role
          </button>
          <span className="ml-auto font-mono text-xs text-mist-400 tnum" aria-live="polite">
            {answeredCount} of {start.questions.length} answered
          </span>
        </div>
      </form>

      <aside className="space-y-3">
        <AgentTimeline steps={start.steps} title="Pipeline: profile and questions" />
        {grounding && <p className="px-1 text-xs text-mist-400">{grounding}</p>}
      </aside>
    </div>
  );
}
