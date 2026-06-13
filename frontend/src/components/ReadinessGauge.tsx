import { useEffect, useState } from "react";

interface Props {
  percent: number;
  threshold: string;
}

/** The hero visual: a radial readiness gauge that sweeps to the score on mount. */
export default function ReadinessGauge({ percent, threshold }: Props) {
  const [shown, setShown] = useState(0);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setShown(percent);
      return;
    }
    let raf = 0;
    const start = performance.now();
    const duration = 1100;
    const tick = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setShown(Math.round(eased * percent));
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [percent]);

  const size = 240;
  const stroke = 18;
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  // 270-degree arc, starting bottom-left.
  const arc = 0.75;
  const circumference = 2 * Math.PI * r;
  const arcLength = circumference * arc;
  const offset = arcLength * (1 - shown / 100);
  const rotation = 135; // start angle so the gap sits at the bottom

  const ready = shown >= 80;
  const band =
    shown >= 80 ? "Role ready" : shown >= 55 ? "Approaching ready" : shown >= 30 ? "Developing" : "Early";
  const bandColor = ready ? "text-emerald-400" : "text-amber-300";

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        role="img"
        aria-label={`Readiness ${percent} percent, ${band}`}
      >
        <defs>
          <linearGradient id="forge" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--color-ember-500)" />
            <stop offset="100%" stopColor="var(--color-amber-300)" />
          </linearGradient>
        </defs>
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="var(--color-ink-700)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${arcLength} ${circumference}`}
          transform={`rotate(${rotation} ${cx} ${cy})`}
        />
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="url(#forge)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={offset}
          transform={`rotate(${rotation} ${cx} ${cy})`}
        />
        <text
          x={cx}
          y={cy - 2}
          textAnchor="middle"
          className="fill-mist-100"
          style={{ fontSize: 62, fontWeight: 600, fontFamily: "var(--font-mono)", fontVariantNumeric: "tabular-nums" }}
        >
          {shown}
        </text>
        <text
          x={cx}
          y={cy + 28}
          textAnchor="middle"
          className="fill-mist-400"
          style={{ fontSize: 12, letterSpacing: "0.18em", fontFamily: "var(--font-mono)" }}
        >
          PERCENT READY
        </text>
      </svg>
      <p className={`mt-1 text-lg font-bold tracking-tight ${bandColor}`}>{band}</p>
      <p className="mt-0.5 text-sm text-mist-400">
        Weighted coverage at the <span className="font-mono text-mist-200">{threshold}</span> bar
      </p>
    </div>
  );
}
