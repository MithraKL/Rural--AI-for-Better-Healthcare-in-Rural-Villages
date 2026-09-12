import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardBody } from "@/components/ui/Card";
import { RiskBadge, Badge } from "@/components/ui/Badge";
import { formatNumber } from "@/lib/format";

const RISK_OPTIONS = ["", "CRITICAL", "HIGH", "MODERATE", "LOW"];

export default function VillageIntelligence() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [districtId, setDistrictId] = useState<number | undefined>(undefined);
  const [riskCategory, setRiskCategory] = useState("");
  const [paradoxOnly, setParadoxOnly] = useState(false);

  const districts = useApi(() => api.districts(), []);
  const villages = useApi(
    () => api.villages({ district_id: districtId, risk_category: riskCategory || undefined, paradox_only: paradoxOnly, search: search || undefined }),
    [districtId, riskCategory, paradoxOnly, search]
  );

  const sorted = useMemo(
    () => [...(villages.data ?? [])].sort((a, b) => (b.overall_gap_score ?? 0) - (a.overall_gap_score ?? 0)),
    [villages.data]
  );

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Village Intelligence</h1>
        <p className="text-sm text-ink-500">Search, filter and drill into every village's full health profile.</p>
      </div>

      <Card>
        <CardBody className="flex flex-wrap items-center gap-3">
          <input
            className="w-56 rounded-lg border border-ink-200 px-3 py-2 text-sm outline-brand-500"
            placeholder="Search village name…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="rounded-lg border border-ink-200 px-3 py-2 text-sm"
            value={districtId ?? ""}
            onChange={(e) => setDistrictId(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">All districts</option>
            {districts.data?.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
          <select
            className="rounded-lg border border-ink-200 px-3 py-2 text-sm"
            value={riskCategory}
            onChange={(e) => setRiskCategory(e.target.value)}
          >
            {RISK_OPTIONS.map((r) => (
              <option key={r} value={r}>{r || "All risk levels"}</option>
            ))}
          </select>
          <label className="flex items-center gap-2 text-sm text-ink-700">
            <input type="checkbox" checked={paradoxOnly} onChange={(e) => setParadoxOnly(e.target.checked)} />
            Hidden gaps only (Infrastructure-Outcome Paradox)
          </label>
          <span className="ml-auto text-xs text-ink-500">{sorted.length} village(s)</span>
        </CardBody>
      </Card>

      <Card>
        <CardBody className="overflow-x-auto p-0">
          <table className="w-full min-w-[720px] text-sm">
            <thead className="bg-ink-50 text-xs uppercase tracking-wide text-ink-500">
              <tr>
                <th className="px-4 py-2.5 text-left">Village</th>
                <th className="px-4 py-2.5 text-left">District</th>
                <th className="px-4 py-2.5 text-right">Population</th>
                <th className="px-4 py-2.5 text-right">Gap Score</th>
                <th className="px-4 py-2.5 text-left">Risk</th>
                <th className="px-4 py-2.5 text-left">Priority</th>
                <th className="px-4 py-2.5 text-left">Flags</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((v) => (
                <tr key={v.id} className="cursor-pointer border-t border-ink-100 hover:bg-ink-50" onClick={() => navigate(`/villages/${v.id}`)}>
                  <td className="px-4 py-2.5 font-medium text-ink-900">{v.name}</td>
                  <td className="px-4 py-2.5 text-ink-600">{v.district_name}</td>
                  <td className="px-4 py-2.5 text-right text-ink-600">{formatNumber(v.population)}</td>
                  <td className="px-4 py-2.5 text-right font-semibold text-ink-900">{v.overall_gap_score?.toFixed(0)}</td>
                  <td className="px-4 py-2.5"><RiskBadge category={v.risk_category} size="sm" /></td>
                  <td className="px-4 py-2.5"><RiskBadge category={v.priority_tier} size="sm" /></td>
                  <td className="px-4 py-2.5">{v.is_paradox && <Badge tone="warn">Hidden Gap</Badge>}</td>
                </tr>
              ))}
              {villages.loading && (
                <tr><td colSpan={7} className="px-4 py-6 text-center text-ink-500">Loading villages…</td></tr>
              )}
              {!villages.loading && sorted.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-6 text-center text-ink-500">No villages match these filters.</td></tr>
              )}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
