import clsx from "clsx";
import type { ReactNode } from "react";
import { riskColor } from "@/lib/format";

export function RiskBadge({ category, size = "md" }: { category?: string | null; size?: "sm" | "md" }) {
  if (!category) return <span className="text-xs text-ink-400">—</span>;
  const c = riskColor(category);
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full font-semibold ring-1",
        c.bg, c.text, c.ring,
        size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs"
      )}
    >
      <span className={clsx("h-1.5 w-1.5 rounded-full", c.dot)} />
      {category}
    </span>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "brand" | "warn" }) {
  const tones: Record<string, string> = {
    neutral: "bg-ink-100 text-ink-700",
    brand: "bg-brand-500/10 text-brand-700",
    warn: "bg-amber-100 text-amber-800",
  };
  return <span className={clsx("inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium", tones[tone])}>{children}</span>;
}
