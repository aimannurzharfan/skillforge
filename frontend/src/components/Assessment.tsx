import { useState } from "react";
import type { AssessmentStart } from "../types";
import AgentTimeline from "./AgentTimeline";
import { Kicker } from "./ui";

interface Props {
  start: AssessmentStart;
  submitting: boolean;
  onSubmit: (answers: { competency_id: string; question: string; answer: string }[]) => void;
  onBack: () => void;
}

export default function Assessment({ start, submitting, onSubmit, onBack }: Props) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const answeredCount = start.questions.filter((q) => (answers[q.competency_id] ?? "").trim().length > 0).length;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = start.questions.map((q) => ({
      competency_id: q.competency_id,
      question: q.question,
      answer: answers[q.competency_id] ?? "",
    }));
    onSubmit(payload);
  };

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
      <form onSubmit={handleSubmit} aria-labelledby="assess-heading">
        <Kicker>Step 2 — mock assessment</Kicker>
        <h1 id="assess-heading" className="mt-2 font-display text-3xl font-bold text-mist-200">
          {start.role.name}
        </h1>
        <p className="mt-2 max-w-2xl text-mist-400">
          Answer in your own words. There is no time limit and partial answers are fine — the assessor grades
          each one on the none / aware / working / proficient scale.
        </p>

        <ol className="mt-8 space-y-5">
          {start.questions.map((q, i) => (
            <li key={q.competency_id} className="panel rounded-2xl p-5">
              <div className="flex items-center justify-between gap-3">
                <span className="font-mono text-xs uppercase tracking-wider text-ember-400">
                  {q.competency_name}
                </span>
                <span className="font-mono text-[0.65rem] text-mist-400">
                  {i + 1} / {start.questions.length}
                </span>
              </div>
              <label htmlFor={`q-${q.competency_id}`} className="mt-2 block font-display text-lg text-mist-200">
                {q.question}
              </label>
              <textarea
                id={`q-${q.competency_id}`}
                value={answers[q.competency_id] ?? ""}
                onChange={(e) => setAnswers((a) => ({ ...a, [q.competency_id]: e.target.value }))}
                rows={3}
                maxLength={4000}
                placeholder="Type your answer…"
                className="mt-3 w-full resize-y rounded-xl border border-ink-600 bg-ink-900/60 p-3 text-mist-200 placeholder:text-mist-400/60 focus:border-amber-300 focus:outline-none"
              />
            </li>
          ))}
        </ol>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={submitting || answeredCount === 0}
            className="rounded-xl bg-gradient-to-r from-ember-500 to-amber-300 px-6 py-3 font-display font-semibold text-ink-950 transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {submitting ? "Scoring with the agents…" : "See my readiness →"}
          </button>
          <button type="button" onClick={onBack} disabled={submitting} className="font-mono text-xs uppercase tracking-wider text-mist-400 hover:text-mist-200">
            ← Change role
          </button>
          <span className="ml-auto font-mono text-xs text-mist-400" aria-live="polite">
            {answeredCount} of {start.questions.length} answered
          </span>
        </div>
      </form>

      <aside className="space-y-4">
        <AgentTimeline steps={start.steps} title="Agents · profile & questions" />
        <p className="px-1 font-mono text-[0.65rem] text-mist-400">
          Knowledge backend: <span className="text-mist-200">{start.knowledge_backend}</span>
        </p>
      </aside>
    </div>
  );
}
