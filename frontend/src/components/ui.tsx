import type { ReactNode } from "react";
import type { StepMode } from "../types";
import { LEVELS } from "./levels";

/** A small mono label. Used once per region, never as a per-section eyebrow. */
export function Label({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <span className={`label text-mist-400 ${className}`}>{children}</span>;
}

export function ModeBadge({ mode }: { mode: StepMode }) {
  const map: Record<StepMode, { label: string; cls: string }> = {
    model: { label: "Phi-4", cls: "text-steel-400 border-steel-400/30" },
    deterministic: { label: "deterministic", cls: "text-emerald-400 border-emerald-400/30" },
    code: { label: "code", cls: "text-mist-300 border-ink-600" },
    none: { label: "skipped", cls: "text-mist-400 border-ink-600" },
  };
  const { label, cls } = map[mode];
  return (
    <span className={`label rounded border px-1.5 py-0.5 text-[0.6rem] tracking-[0.1em] ${cls}`}>
      {label}
    </span>
  );
}

/** Four-segment indicator: attained against the target on the competency scale. */
export function LevelMeter({ attained, target }: { attained: number; target: number }) {
  const met = attained >= target;
  return (
    <div
      className="flex items-center gap-1"
      role="img"
      aria-label={`Level ${LEVELS[attained]} of target ${LEVELS[target]}`}
    >
      {LEVELS.map((_, i) => {
        const filled = i <= attained && attained > 0;
        const isTarget = i === target;
        return (
          <span
            key={i}
            className={[
              "h-1.5 w-7 rounded-full transition-colors",
              filled ? (met ? "bg-emerald-400" : "bg-ember-500") : "bg-ink-700",
              isTarget && !filled ? "ring-1 ring-inset ring-mist-400/50" : "",
            ].join(" ")}
          />
        );
      })}
    </div>
  );
}

export function LevelTag({ level }: { level: string }) {
  return <span className="font-mono text-xs uppercase tracking-wide text-mist-300">{level}</span>;
}
