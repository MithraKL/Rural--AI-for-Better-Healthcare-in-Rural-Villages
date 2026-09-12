import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/Badge";
import { formatNumber } from "@/lib/format";

const INDICATORS = [
  { key: "malnutrition", label: "Malnutrition" },
  { key: "immunization", label: "Immunization decline" },
  { key: "overall_risk", label: "Overall risk" },
] as const;

export default function HiddenGaps() {
  const navigate = useNavigate();
  const [indicator, setIndicator] = useState<(typeof INDICATORS)[number]["key"]>("malnutrition");

  const paradoxVillages = useApi(() => api.villages({ paradox_only: true }), []);
  const warnings = useApi(() => api.earlyWarnings(indicator), [indicator]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Hidden Gaps</h1>
        <p className="text-sm text-ink-500">
          The signature RuralCare AI finding: villages where infrastructure looks adequate but healthcare delivery
          isn't happening — plus early warnings on trends that haven't become critical yet.
        </p>
      </div>

      <Card>
        <CardHeader
          title="Infrastructure-Outcome Paradox"
          subtitle="High infrastructure availability + poor service delivery / utilization / outcomes. Associated pattern, not a proven cause — requires field validation."
        />
        <CardBody className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {paradoxVillages.loading && <p className="text-sm text-ink-500">Loading…</p>}
          {paradoxVillages.data?.length === 0 && <p className="text-sm text-ink-500">No paradox villages detected in the current data.</p>}
          {paradoxVillages.data?.map((v) => (
            <div
              key={v.id}
              onClick={() => navigate(`/villages/${v.id}`)}
              className="cursor-pointer rounded-xl border border-amber-200 bg-amber-50 p-4 hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <p className="font-semibold text-amber-900">{v.name}</p>
                <RiskBadge category={v.risk_category} size="sm" />
              </div>
              <p className="text-xs text-amber-700">{v.district_name} · {formatNumber(v.population)} people</p>
              <p className="mt-2 text-xs font-medium text-amber-800">Infrastructure adequate — outcomes lagging ⚠</p>
            </div>
          ))}
        </CardBody>
      </Card>

      <Card>
        <CardHeader
          title="Early Warning System"
          subtitle="Statistically consistent worsening trends, with projected periods until a high-risk threshold is crossed"
          action={
            <div className="flex gap-1">
              {INDICATORS.map((i) => (
                <button
                  key={i.key}
                  onClick={() => setIndicator(i.key)}
                  className={`rounded-md px-2.5 py-1 text-xs font-medium ${indicator === i.key ? "bg-brand-600 text-white" : "bg-ink-100 text-ink-600"}`}
                >
                  {i.label}
                </button>
              ))}
            </div>
          }
        />
        <CardBody className="space-y-3">
          {warnings.loading && <p className="text-sm text-ink-500">Loading…</p>}
          {warnings.data?.length === 0 && <p className="text-sm text-ink-500">No worsening trends detected for this indicator.</p>}
          {warnings.data?.map((w) => (
            <div key={w.village_id} onClick={() => navigate(`/villages/${w.village_id}`)} className="cursor-pointer rounded-lg border border-ink-200 p-3 hover:bg-ink-50">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-ink-900">{w.village_name}</p>
                {w.periods_to_threshold && (
                  <span className="rounded-full bg-red-100 px-2 py-0.5 text-[11px] font-semibold text-red-700">
                    ~{w.periods_to_threshold} quarter(s) to threshold
                  </span>
                )}
              </div>
              <p className="mt-1 text-xs text-ink-600">{w.message}</p>
            </div>
          ))}
        </CardBody>
      </Card>
    </div>
  );
}
