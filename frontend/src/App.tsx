import { useEffect, useState } from "react";
import { fetchRoles, startAssessment, submitAnswers } from "./api";
import type { AssessmentStart, ResultData, RoleSummary } from "./types";
import { groundingLabel } from "./types";
import RolePicker from "./components/RolePicker";
import Assessment from "./components/Assessment";
import Result from "./components/Result";
import Logo from "./components/Logo";

type Stage = "pick" | "assess" | "result";

const STEPS: { id: Stage; label: string }[] = [
  { id: "pick", label: "Target role" },
  { id: "assess", label: "Assessment" },
  { id: "result", label: "Readiness" },
];

function Stepper({ stage }: { stage: Stage }) {
  const current = STEPS.findIndex((s) => s.id === stage);
  return (
    <ol className="flex items-center gap-2" aria-label="Progress">
      {STEPS.map((s, i) => {
        const state = i < current ? "done" : i === current ? "current" : "todo";
        return (
          <li key={s.id} className="flex items-center gap-2">
            <span
              aria-current={state === "current" ? "step" : undefined}
              className={[
                "label flex items-center gap-1.5 rounded-full px-2.5 py-1 transition-colors",
                state === "current"
                  ? "bg-ember-500/15 text-ember-400"
                  : state === "done"
                    ? "text-mist-300"
                    : "text-mist-400/70",
              ].join(" ")}
            >
              <span
                aria-hidden="true"
                className={[
                  "h-1.5 w-1.5 rounded-full",
                  state === "current"
                    ? "bg-ember-500"
                    : state === "done"
                      ? "bg-emerald-400"
                      : "bg-ink-600",
                ].join(" ")}
              />
              {s.label}
            </span>
            {i < STEPS.length - 1 && <span aria-hidden="true" className="h-px w-4 bg-ink-700" />}
          </li>
        );
      })}
    </ol>
  );
}

export default function App() {
  const [roles, setRoles] = useState<RoleSummary[]>([]);
  const [backend, setBackend] = useState<string | null>(null);
  const [stage, setStage] = useState<Stage>("pick");
  const [start, setStart] = useState<AssessmentStart | null>(null);
  const [result, setResult] = useState<ResultData | null>(null);
  const [busyRoleId, setBusyRoleId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRoles()
      .then((data) => {
        setRoles(data.roles);
        setBackend(data.knowledge_backend);
      })
      .catch((e) => setError(String(e.message ?? e)));
  }, []);

  const pickRole = async (roleId: string) => {
    setError(null);
    setBusyRoleId(roleId);
    try {
      const data = await startAssessment(roleId);
      setStart(data);
      setStage("assess");
      window.scrollTo({ top: 0 });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusyRoleId(null);
    }
  };

  const submit = async (answers: { competency_id: string; question: string; answer: string }[]) => {
    if (!start) return;
    setError(null);
    setSubmitting(true);
    try {
      const data = await submitAnswers(start.role.id, answers);
      setResult(data);
      setStage("result");
      window.scrollTo({ top: 0 });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSubmitting(false);
    }
  };

  const restart = () => {
    setStage("pick");
    setStart(null);
    setResult(null);
    window.scrollTo({ top: 0 });
  };

  const grounding = groundingLabel(backend);

  return (
    <div className="mx-auto min-h-screen max-w-5xl px-5 py-6 sm:px-8 sm:py-9">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Logo className="h-9 w-9 shrink-0" />
          <div className="leading-tight">
            <p className="text-[1.05rem] font-bold tracking-tight text-mist-100">SkillForge</p>
            <p className="text-xs text-mist-400">Role readiness, scored and grounded</p>
          </div>
        </div>
        {grounding && (
          <span className="label flex items-center gap-2 text-mist-400">
            <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-steel-400" />
            {grounding}
          </span>
        )}
      </header>

      <div className="mt-6 border-y border-ink-700/70 py-3">
        <Stepper stage={stage} />
      </div>

      {error && (
        <div
          role="alert"
          className="mt-6 rounded-xl border border-ember-500/50 bg-ember-500/10 px-4 py-3 text-sm text-amber-300"
        >
          {error}
        </div>
      )}

      <main className="mt-8">
        {stage === "pick" && <RolePicker roles={roles} busyRoleId={busyRoleId} onPick={pickRole} />}
        {stage === "assess" && start && (
          <Assessment start={start} submitting={submitting} onSubmit={submit} onBack={restart} />
        )}
        {stage === "result" && result && <Result data={result} onRestart={restart} />}
      </main>

      <footer className="mt-14 border-t border-ink-700 pt-6 text-xs text-mist-400">
        Phi-4-mini-instruct on Microsoft Foundry. Readiness is computed in code, never by the model.
      </footer>
    </div>
  );
}
