import { useParams, useNavigate, Link } from "react-router-dom";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { RiskBadge, Badge } from "@/components/ui/Badge";
import GapRadar from "@/components/charts/GapRadar";
import TrendChart from "@/components/charts/TrendChart";
import DriverBars from "@/components/charts/DriverBars";
import { formatINR, formatNumber } from "@/lib/format";

const DIM_LABELS: [string, string][] = [
  ["infrastructure_score", "Infrastructure"],
  ["workforce_score", "Workforce"],
  ["service_score", "Service Delivery"],
  ["utilization_score", "Utilization"],
  ["outcome_score", "Health Outcomes"],
  ["nutrition_score", "Nutrition"],
  ["accessibility_score", "Accessibility"],
];

export default function VillageProfile() {
  const { id } = useParams();
  const villageId = Number(id);
  const navigate = useNavigate();

  const village = useApi(() => api.village(villageId), [villageId]);
  const prediction = useApi(() => api.prediction(villageId), [villageId]);
  const explanation = useApi(() => api.explanation(villageId), [villageId]);
  const interventions = useApi(() => api.interventions(villageId), [villageId]);

  if (village.loading) return <p className="text-sm text-ink-500">Loading village profile…</p>;
  if (village.error || !village.data) return <p className="text-sm text-red-600">Could not load village: {village.error}</p>;

  const v = village.data;
  const gap = v.gap_breakdown;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => navigate(-1)} className="text-xs text-ink-500 hover:underline">&larr; Back</button>
          <h1 className="text-xl font-bold text-ink-900">{v.name}</h1>
          <p className="text-sm text-ink-500">{v.block_name}, {v.district_name}, {v.state_name} · Population {formatNumber(v.population)}</p>
        </div>
        <div className="flex gap-2">
          <Link to={`/simulator?village=${v.id}`} className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">
            Open What-If Simulator
          </Link>
        </div>
      </div>

      {v.is_paradox && gap?.paradox_note && (
        <Card className="border-amber-300 bg-amber-50">
          <CardBody className="flex gap-3">
            <span className="text-2xl">⚠</span>
            <div>
              <p className="text-sm font-bold text-amber-900">Hidden Healthcare Gap — Infrastructure-Outcome Paradox</p>
              <p className="mt-1 text-sm text-amber-800">{gap.paradox_note}</p>
            </div>
          </CardBody>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Overall Risk" subtitle={gap ? `As of ${gap.quarter}` : undefined} />
          <CardBody className="flex items-center justify-between">
            <div>
              <p className="text-4xl font-bold text-ink-900">{gap?.overall_gap_score.toFixed(0) ?? "—"}<span className="text-lg text-ink-400">/100</span></p>
              <div className="mt-2"><RiskBadge category={v.risk_category} /></div>
            </div>
            {prediction.data && !prediction.data.insufficient_data && (
              <div className="text-right">
                <p className="text-xs text-ink-500">Predicted next quarter</p>
                <p className="text-2xl font-bold text-ink-900">{prediction.data.predicted_risk.toFixed(0)}</p>
                <p className="text-xs font-medium text-ink-500">{prediction.data.trend_direction} · {(prediction.data.confidence * 100).toFixed(0)}% confidence</p>
              </div>
            )}
          </CardBody>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Dimension Breakdown" subtitle="Each dimension normalized 0-100; higher = better" />
          <CardBody>
            {gap && (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {DIM_LABELS.map(([key, label]) => (
                  <div key={key} className="rounded-lg bg-ink-50 p-3">
                    <p className="text-[11px] font-medium uppercase text-ink-500">{label}</p>
                    <p className="text-xl font-bold text-ink-900">{(gap as any)[key].toFixed(0)}</p>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Dimension Radar" />
          <CardBody>{gap && <GapRadar scores={gap} />}</CardBody>
        </Card>
        <Card>
          <CardHeader title="Historical Trend" subtitle="Overall gap/risk score by quarter" />
          <CardBody>
            <TrendChart
              data={v.trend.map((t) => ({ quarter: t.quarter, "Overall Risk": t.overall_gap_score, "Utilization": t.utilization_score, "Nutrition": t.nutrition_score }))}
              series={[
                { key: "Overall Risk", label: "Overall Risk", color: "#b91c1c" },
                { key: "Utilization", label: "Utilization", color: "#137a73" },
                { key: "Nutrition", label: "Nutrition", color: "#c2410c" },
              ]}
            />
          </CardBody>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Why is this village at risk?" subtitle="Model-based feature contribution (interpretable ML, not a black box)" />
          <CardBody>
            {prediction.loading && <p className="text-sm text-ink-500">Loading…</p>}
            {prediction.data?.insufficient_data && (
              <p className="text-sm text-ink-500">Insufficient historical data for a reliable prediction/explanation yet.</p>
            )}
            {prediction.data && !prediction.data.insufficient_data && <DriverBars factors={prediction.data.factors} />}
            {explanation.data && (
              <p className="mt-4 rounded-lg bg-ink-50 p-3 text-sm text-ink-700">{explanation.data.narrative}</p>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Recommended Actions" subtitle="Ranked by model-estimated impact per resource" />
          <CardBody className="space-y-3">
            {interventions.loading && <p className="text-sm text-ink-500">Loading…</p>}
            {interventions.data?.length === 0 && <p className="text-sm text-ink-500">No specific problems detected for the latest quarter.</p>}
            {interventions.data?.map((opt) => (
              <div key={opt.id} className="rounded-lg border border-ink-200 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-ink-900">{opt.rank}. {opt.intervention_name}</p>
                  {opt.is_infrastructure_expansion && <Badge tone="warn">Infrastructure expansion</Badge>}
                </div>
                <p className="mt-0.5 text-xs text-ink-500">Addresses: {opt.problem_tag.replaceAll("_", " ").toLowerCase()}</p>
                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-600">
                  <span>Cost: <b>{opt.cost_level}</b> ({formatINR(opt.cost_estimate_inr)})</span>
                  <span>Time: <b>{opt.time_months} mo</b></span>
                  <span>Coverage: <b>{formatNumber(opt.coverage_population)}</b></span>
                  <span>Impact/Resource: <b>{opt.impact_per_resource.toFixed(1)}</b></span>
                </div>
              </div>
            ))}
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader title="Facilities in this village" />
        <CardBody className="overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-ink-50 text-xs uppercase text-ink-500">
              <tr>
                <th className="px-4 py-2 text-left">Name</th>
                <th className="px-4 py-2 text-left">Type</th>
                <th className="px-4 py-2 text-right">Doctors</th>
                <th className="px-4 py-2 text-right">Nurses</th>
                <th className="px-4 py-2 text-right">Beds</th>
                <th className="px-4 py-2 text-right">Monthly Capacity</th>
                <th className="px-4 py-2 text-left">Medicine Stock</th>
              </tr>
            </thead>
            <tbody>
              {v.facilities.map((f) => (
                <tr key={f.id} className="border-t border-ink-100">
                  <td className="px-4 py-2 font-medium">{f.name}</td>
                  <td className="px-4 py-2">{f.facility_type}</td>
                  <td className="px-4 py-2 text-right">{f.doctors_in_position}/{f.doctors_sanctioned}</td>
                  <td className="px-4 py-2 text-right">{f.nurses_in_position}/{f.nurses_sanctioned}</td>
                  <td className="px-4 py-2 text-right">{f.beds}</td>
                  <td className="px-4 py-2 text-right">{formatNumber(f.monthly_patient_capacity)}</td>
                  <td className="px-4 py-2">{f.has_medicine_stock ? <Badge tone="brand">Available</Badge> : <Badge tone="warn">Shortage</Badge>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
