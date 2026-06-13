import type { RoleSummary } from "../types";
import { Kicker } from "./ui";

interface Props {
  roles: RoleSummary[];
  busyRoleId: string | null;
  onPick: (roleId: string) => void;
}

export default function RolePicker({ roles, busyRoleId, onPick }: Props) {
  const nameById = new Map(roles.map((r) => [r.id, r.name]));
  return (
    <section aria-labelledby="picker-heading">
      <Kicker>Step 1 — choose a target role</Kicker>
      <h1 id="picker-heading" className="mt-2 font-display text-3xl font-bold text-mist-200 sm:text-4xl">
        Get ready for the role.
      </h1>
      <p className="mt-2 max-w-2xl text-mist-400">
        Pick a role and take a short mock assessment. SkillForge scores you against the role's competency
        profile, finds the gaps, and builds a grounded learning plan with citations.
      </p>

      <ul className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {roles.map((role) => {
          const busy = busyRoleId === role.id;
          return (
            <li key={role.id}>
              <button
                type="button"
                onClick={() => onPick(role.id)}
                disabled={busyRoleId !== null}
                aria-busy={busy}
                className="group panel relative flex h-full w-full flex-col rounded-2xl p-5 text-left transition-colors hover:border-ember-500/60 disabled:cursor-wait disabled:opacity-60"
              >
                <div className="flex items-start justify-between gap-3">
                  <h2 className="font-display text-lg font-semibold text-mist-200">{role.name}</h2>
                  <span className="font-mono text-[0.65rem] text-mist-400">
                    {role.competency_count} comps
                  </span>
                </div>
                <p className="mt-2 flex-1 text-sm text-mist-400">{role.summary}</p>
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {role.builds_on && (
                    <span className="rounded-full border border-steel-400/40 bg-steel-400/10 px-2 py-0.5 font-mono text-[0.62rem] text-steel-400">
                      builds on {nameById.get(role.builds_on) ?? role.builds_on}
                    </span>
                  )}
                  {role.foundational_tools.slice(0, 3).map((t) => (
                    <span key={t} className="rounded-full border border-ink-600 bg-white/5 px-2 py-0.5 font-mono text-[0.62rem] text-mist-400">
                      {t}
                    </span>
                  ))}
                </div>
                <span className="mt-4 inline-flex items-center gap-1 font-mono text-xs uppercase tracking-wider text-ember-400 group-hover:text-ember-500">
                  {busy ? "Preparing assessment…" : "Start assessment →"}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
