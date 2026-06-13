import type { RoleSummary } from "../types";

interface Props {
  roles: RoleSummary[];
  busyRoleId: string | null;
  onPick: (roleId: string) => void;
}

export default function RolePicker({ roles, busyRoleId, onPick }: Props) {
  const nameById = new Map(roles.map((r) => [r.id, r.name]));
  const busy = busyRoleId !== null;

  return (
    <section aria-labelledby="picker-heading">
      <h1
        id="picker-heading"
        className="max-w-2xl text-3xl font-extrabold leading-[1.1] tracking-tight text-mist-100 text-balance sm:text-[2.6rem]"
      >
        Measure your readiness for a role.
      </h1>
      <p className="mt-3 max-w-xl text-[0.95rem] leading-relaxed text-mist-300">
        Pick a target role and answer a short assessment. SkillForge scores you against its
        competency profile, finds the gaps, and builds a cited learning plan to close them.
      </p>

      <div className="mt-9 overflow-hidden rounded-2xl border border-ink-700">
        <ul className="divide-y divide-ink-700">
          {roles.map((role) => {
            const thisBusy = busyRoleId === role.id;
            return (
              <li key={role.id}>
                <button
                  type="button"
                  onClick={() => onPick(role.id)}
                  disabled={busy}
                  aria-busy={thisBusy}
                  className="group flex w-full items-center gap-5 bg-ink-850 px-5 py-4 text-left transition-colors hover:bg-ink-800 focus-visible:bg-ink-800 disabled:cursor-wait disabled:opacity-60 sm:px-6"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                      <h2 className="text-base font-semibold text-mist-100">{role.name}</h2>
                      {role.builds_on && (
                        <span className="text-xs text-mist-400">
                          Builds on {nameById.get(role.builds_on) ?? role.builds_on}
                        </span>
                      )}
                    </div>
                    <p className="mt-1 truncate text-sm text-mist-300">{role.summary}</p>
                  </div>

                  <span className="hidden shrink-0 font-mono text-xs text-mist-400 tnum sm:block">
                    {role.competency_count} competencies
                  </span>

                  <span
                    aria-hidden="true"
                    className="shrink-0 font-mono text-lg text-mist-400 transition-all group-hover:translate-x-0.5 group-hover:text-ember-400"
                  >
                    {thisBusy ? "..." : "→"}
                  </span>
                </button>
              </li>
            );
          })}
          {roles.length === 0 && (
            <li className="bg-ink-850 px-6 py-10 text-center text-sm text-mist-400">
              Loading roles...
            </li>
          )}
        </ul>
      </div>
    </section>
  );
}
