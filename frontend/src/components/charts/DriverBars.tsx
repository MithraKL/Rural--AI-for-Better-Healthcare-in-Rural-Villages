import type { RiskFactor } from "@/types";

export default function DriverBars({ factors }: { factors: RiskFactor[] }) {
  const sorted = [...factors].sort((a, b) => b.contribution_pct - a.contribution_pct);
  return (
    <div className="space-y-2.5">
      {sorted.map((f) => (
        <div key={f.factor_name}>
          <div className="mb-1 flex items-center justify-between text-xs">
            <span className="font-medium text-ink-700">
              {f.factor_name} <span className="text-ink-400">({f.direction === "increases" ? "increases risk" : "protective"})</span>
            </span>
            <span className="font-semibold text-ink-900">{f.contribution_pct.toFixed(0)}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-ink-100">
            <div
              className={`h-full rounded-full ${f.direction === "increases" ? "bg-red-500" : "bg-emerald-500"}`}
              style={{ width: `${Math.min(f.contribution_pct, 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
