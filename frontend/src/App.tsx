import { useEffect, useState } from "react";
import { fetchRoles, startAssessment, submitAnswers } from "./api";
import type { AssessmentStart, ResultData, RoleSummary } from "./types";
import RolePicker from "./components/RolePicker";
import Assessment from "./components/Assessment";
import Result from "./components/Result";

type Stage = "pick" | "assess" | "result";

export default function App() {
  const [roles, setRoles] = useState<RoleSummary[]>([]);
  const [stage, setStage] = useState<Stage>("pick");
  const [start, setStart] = useState<AssessmentStart | null>(null);
  const [result, setResult] = useState<ResultData | null>(null);
  const [busyRoleId, setBusyRoleId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRoles().then(setRoles).catch((e) => setError(String(e.message ?? e)));
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

  return (
    <div className="mx-auto min-h-screen max-w-6xl px-4 py-6 sm:px-6 sm:py-10">
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span aria-hidden="true" className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-ember-500 to-amber-300 font-display text-lg font-bold text-ink-950">
            S
          </span>
          <div>
            <p className="font-display text-lg font-bold tracking-tight text-mist-200">SkillForge</p>
            <p className="font-mono text-[0.62rem] uppercase tracking-[0.2em] text-mist-400">
              Role readiness agent
            </p>
          </div>
        </div>
        <a
          href="/health"
          className="font-mono text-[0.65rem] uppercase tracking-wider text-mist-400 hover:text-steel-400"
        >
          status
        </a>
      </header>

      {error && (
        <div role="alert" className="mb-6 rounded-xl border border-ember-500/50 bg-ember-500/10 px-4 py-3 text-sm text-amber-300">
          {error}
        </div>
      )}

      <main>
        {stage === "pick" && <RolePicker roles={roles} busyRoleId={busyRoleId} onPick={pickRole} />}
        {stage === "assess" && start && (
          <Assessment start={start} submitting={submitting} onSubmit={submit} onBack={restart} />
        )}
        {stage === "result" && result && <Result data={result} onRestart={restart} />}
      </main>

      <footer className="mt-12 border-t border-ink-700 pt-6 font-mono text-[0.65rem] text-mist-400">
        Phi-4-mini-instruct on Microsoft Foundry · grounded via Foundry IQ or the local seed corpus ·
        deterministic readiness math
      </footer>
    </div>
  );
}
