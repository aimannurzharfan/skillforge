/** The SkillForge mark: a readiness gauge arc swept to a forge spark, in ember.
 *  It echoes the hero ReadinessGauge so the brand reads as "readiness, scored". */
export default function Logo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      role="img"
      aria-label="SkillForge"
    >
      <path
        d="M7.87 24.13 A11.5 11.5 0 1 1 24.13 24.13"
        fill="none"
        stroke="var(--color-ember-500)"
        strokeWidth="3.4"
        strokeLinecap="round"
      />
      <line
        x1="16"
        y1="16"
        x2="22.3"
        y2="10.3"
        stroke="var(--color-ember-500)"
        strokeWidth="2.6"
        strokeLinecap="round"
      />
      <circle cx="16" cy="16" r="2.2" fill="var(--color-ember-500)" />
      <path
        d="M23 6.2 L23.78 9.22 L26.8 10 L23.78 10.78 L23 13.8 L22.22 10.78 L19.2 10 L22.22 9.22 Z"
        fill="var(--color-amber-300)"
      />
    </svg>
  );
}
