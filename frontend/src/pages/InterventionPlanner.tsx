import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatINR, formatNumber } from "@/lib/format";

export default function InterventionPlanner() {
  const navigate = useNavigate();
  const [villageId, setVillageId] = useState<number | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  const villages = useApi(() => api.villages(), []);
  const interventions = useApi(() => (villageId ? api.interventions(villageId) : Promise.resolve([])), [villageId]);

  function toggle(id: number) {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Intervention Planner</h1>
        <p className="text-sm text-ink-500">
          Concrete, problem-mapped interventions — never generic advice — ranked by model-estimated impact per resource.
          Infrastructure expansion is only proposed when the Infrastructure dimension itself is genuinely poor.
        </p>
      </div>

      <Card>
        <CardBody className="flex flex-wrap items-center gap-3">
          <select
            className="w-64 rounded-lg border border-ink-200 px-3 py-2 text-sm"
            value={villageId ?? ""}
            onChange={(e) => { setVillageId(e.target.value ? Number(e.target.value) : null); setSelectedIds([]); }}
          >
            <option value="">Select a village…</option>
            {villages.data?.map((v) => (
              <option key={v.id} value={v.id}>{v.name} — {v.district_name} ({v.risk_category})</option>
            ))}
          </select>
          {selectedIds.length > 0 && (
            <button
              className="ml-auto rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
              onClick={() => navigate(`/simulator?village=${villageId}&interventions=${selectedIds.join(",")}`)}
            >
              Compare {selectedIds.length} option(s) in What-If Simulator →
            </button>
          )}
        </CardBody>
      </Card>

      {villageId && (
        <Card>
          <CardHeader title="Ranked Intervention Options" subtitle="Select two or more to compare in the simulator" />
          <CardBody className="overflow-x-auto p-0">
            <table className="w-full min-w-[860px] text-sm">
              <thead className="bg-ink-50 text-xs uppercase text-ink-500">
                <tr>
                  <th className="px-4 py-2 text-left">Select</th>
                  <th className="px-4 py-2 text-left">Rank</th>
                  <th className="px-4 py-2 text-left">Intervention</th>
                  <th className="px-4 py-2 text-left">Problem</th>
                  <th className="px-4 py-2 text-right">Cost</th>
                  <th className="px-4 py-2 text-right">Time</th>
                  <th className="px-4 py-2 text-right">Expected Impact</th>
                  <th className="px-4 py-2 text-right">Impact/Resource</th>
                  <th className="px-4 py-2 text-right">Coverage</th>
                </tr>
              </thead>
              <tbody>
                {interventions.data?.map((opt) => (
                  <tr key={opt.id} className="border-t border-ink-100">
                    <td className="px-4 py-2">
                      <input type="checkbox" checked={selectedIds.includes(opt.id)} onChange={() => toggle(opt.id)} />
                    </td>
                    <td className="px-4 py-2 font-semibold">{opt.rank}</td>
                    <td className="px-4 py-2">
                      <p className="font-medium text-ink-900">{opt.intervention_name}</p>
                      {opt.is_infrastructure_expansion && <Badge tone="warn">Infrastructure expansion</Badge>}
                    </td>
                    <td className="px-4 py-2 text-ink-600">{opt.problem_tag.replaceAll("_", " ").toLowerCase()}</td>
                    <td className="px-4 py-2 text-right">{opt.cost_level}<br /><span className="text-xs text-ink-400">{formatINR(opt.cost_estimate_inr)}</span></td>
                    <td className="px-4 py-2 text-right">{opt.time_months} mo</td>
                    <td className="px-4 py-2 text-right font-semibold">{opt.expected_impact_score.toFixed(0)}</td>
                    <td className="px-4 py-2 text-right">{opt.impact_per_resource.toFixed(1)}</td>
                    <td className="px-4 py-2 text-right">{formatNumber(opt.coverage_population)}</td>
                  </tr>
                ))}
                {interventions.data?.length === 0 && !interventions.loading && (
                  <tr><td colSpan={9} className="px-4 py-6 text-center text-ink-500">No specific problems detected for this village.</td></tr>
                )}
              </tbody>
            </table>
          </CardBody>
        </Card>
      )}
      <p className="text-xs text-ink-400">
        All figures are model-estimated / projected impact based on the intervention catalogue and current indicators — not guaranteed real-world results.
      </p>
    </div>
  );
}
