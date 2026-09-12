import clsx from "clsx";

export function StatTile({
  label, value, sublabel, tone = "neutral",
}: { label: string; value: string | number; sublabel?: string; tone?: "neutral" | "critical" | "warn" | "good" | "brand" }) {
  const tones: Record<string, string> = {
    neutral: "text-ink-900",
    critical: "text-red-700",
    warn: "text-orange-600",
    good: "text-emerald-700",
    brand: "text-brand-700",
  };
  return (
    <div className="rounded-xl border border-ink-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-ink-500">{label}</p>
      <p className={clsx("mt-1.5 text-2xl font-bold tabular-nums", tones[tone])}>{value}</p>
      {sublabel && <p className="mt-1 text-xs text-ink-400">{sublabel}</p>}
    </div>
  );
}
