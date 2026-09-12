import { useNavigate } from "react-router-dom";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { StatTile } from "@/components/ui/StatTile";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/Badge";
import VillageMap from "@/components/map/VillageMap";
import { formatNumber } from "@/lib/format";

export default function Overview() {
  const navigate = useNavigate();
  const kpis = useApi(() => api.dashboardKpis(), []);
  const villages = useApi(() => api.villages(), []);
  const priorities = useApi(() => api.priorities({ tier: undefined }), []);

  const topPriorities = (priorities.data ?? []).slice(0, 8);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Decision Overview</h1>
        <p className="text-sm text-ink-500">
          Where is the problem, why is it happening, what will happen next, what should we do, and where should
          resources go — answered in one view.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        <StatTile label="Critical Villages" value={kpis.data?.critical_villages ?? "—"} tone="critical" />
        <StatTile label="Emerging Risk" value={kpis.data?.emerging_risk_villages ?? "—"} tone="warn" />
        <StatTile
          label="At-Risk Population"
          value={kpis.data ? formatNumber(kpis.data.at_risk_population) : "—"}
          tone="critical"
        />
        <StatTile label="High-Risk Facilities" value={kpis.data?.high_risk_facilities ?? "—"} tone="warn" />
        <StatTile
          label="Resource Utilization"
          value={kpis.data ? `${kpis.data.resource_utilization_pct.toFixed(0)}%` : "—"}
          tone="brand"
        />
        <StatTile
          label="Potential Impact"
          value={kpis.data ? kpis.data.potential_impact_score.toFixed(0) : "—"}
          sublabel="model-estimated"
          tone="good"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader
            title="District Risk Map"
            subtitle={`${kpis.data?.total_villages ?? "—"} villages · latest quarter ${kpis.data?.quarter ?? ""} · circle size = population, ring = Infrastructure-Outcome Paradox`}
          />
          <CardBody>
            {villages.loading ? (
              <p className="text-sm text-ink-500">Loading map…</p>
            ) : (
              <VillageMap villages={villages.data ?? []} onSelect={(v) => navigate(`/villages/${v.id}`)} />
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Top Priority Villages" subtitle="Ranked by risk × population × severity × trend" />
          <CardBody className="max-h-[460px] overflow-y-auto p-0">
            <table className="w-full text-sm">
              <tbody>
                {topPriorities.map((p) => (
                  <tr
                    key={p.village_id}
                    className="cursor-pointer border-b border-ink-100 last:border-0 hover:bg-ink-50"
                    onClick={() => navigate(`/villages/${p.village_id}`)}
                  >
                    <td className="px-4 py-2.5">
                      <p className="font-medium text-ink-900">{p.village_name}</p>
                      <p className="text-xs text-ink-500">{p.district_name} · {formatNumber(p.population_affected)} people</p>
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <RiskBadge category={p.priority_tier} size="sm" />
                    </td>
                  </tr>
                ))}
                {priorities.loading && <tr><td className="px-4 py-3 text-ink-500">Loading…</td></tr>}
              </tbody>
            </table>
          </CardBody>
        </Card>
      </div>

      {kpis.data?.is_demo_data && (
        <p className="text-xs text-ink-400">
          District/village geography and NFHS-5/AHS district indicators below are real published data; facility-level
          utilization and Anganwadi figures are synthetic (see Data Explorer for the source-by-source breakdown).
          Replace synthetic sources with real RHS / HMIS / Anganwadi datasets for deployment.
        </p>
      )}
    </div>
  );
}
