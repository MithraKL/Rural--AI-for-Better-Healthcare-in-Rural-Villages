export function formatINR(value: number): string {
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)} Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(2)} L`;
  if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return `₹${Math.round(value)}`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-IN").format(Math.round(value));
}

export const RISK_COLORS: Record<string, { bg: string; text: string; ring: string; dot: string }> = {
  CRITICAL: { bg: "bg-red-50", text: "text-red-800", ring: "ring-red-200", dot: "bg-red-600" },
  HIGH: { bg: "bg-orange-50", text: "text-orange-800", ring: "ring-orange-200", dot: "bg-orange-500" },
  MODERATE: { bg: "bg-amber-50", text: "text-amber-800", ring: "ring-amber-200", dot: "bg-amber-500" },
  LOW: { bg: "bg-emerald-50", text: "text-emerald-800", ring: "ring-emerald-200", dot: "bg-emerald-600" },
};

export const RISK_MAP_COLOR: Record<string, string> = {
  CRITICAL: "#b91c1c",
  HIGH: "#ea580c",
  MODERATE: "#d97706",
  LOW: "#15803d",
};

export function riskColor(category?: string | null) {
  return RISK_COLORS[category ?? ""] ?? RISK_COLORS.MODERATE;
}
