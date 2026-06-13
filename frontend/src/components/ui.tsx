import type { ReactNode } from "react";
import type { StepMode } from "../types";
import { LEVELS } from "./levels";

export function Kicker({ children }: { children: ReactNode }) {
  return <p className="kicker text-ember-400">{children}</p>;
}

export function ModeBadge({ mode }: { mode: StepMode }) {
  const map: Record<StepMode, { label: string; cls: string }> = {
    model: { label: "Phi-4 model", cls: "border-steel-400/40 bg-steel-400/10 text-steel-400" },
    deterministic: { label: "deterministic", cls: "border-emerald-400/40 bg-emerald-400/10 text-emerald-400" },
    code: { label: "code", cls: "border-mist-400/40 bg-white/5 text-mist-200" },
    none: { label: "skipped", cls: "border-mist-400/30 bg-white/5 text-mist-400" },
  };
  const { label, cls } = map[mode];
  return (
    <span className={`font-mono text-[0.62rem] uppercase tracking-wider rounded-full border px-2 py-0.5 ${cls}`}>
      {label}
    </span>
  );
}

/** Four-segment indicator showing attained vs target on the competency scale. */
export function LevelMeter({ attained, target }: { attained: number; target: number }) {
  return (
    <div className="flex items-center gap-1" role="img" aria-label={`Level ${LEVELS[attained]} of target ${LEVELS[target]}`}>
      {LEVELS.map((_, i) => {
        const filled = i <= attained && attained > 0;
        const isTarget = i === target;
        return (
          <span
            key={i}
            className={[
              "h-2 w-6 rounded-sm transition-colors",
              filled ? (attained >= target ? "bg-emerald-400" : "bg-ember-500") : "bg-ink-600",
              isTarget ? "ring-1 ring-amber-300 ring-offset-1 ring-offset-ink-800" : "",
            ].join(" ")}
          />
        );
      })}
    </div>
  );
}

export function LevelTag({ level }: { level: string }) {
  return <span className="font-mono text-xs uppercase tracking-wide text-mist-200">{level}</span>;
}
