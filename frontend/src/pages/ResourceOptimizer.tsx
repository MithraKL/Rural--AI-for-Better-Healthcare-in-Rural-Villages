import { useState } from "react";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { StatTile } from "@/components/ui/StatTile";
import { formatINR, formatNumber } from "@/lib/format";
import type { ResourceOptimizationResult, ResourcePoolIn } from "@/types";

const DEFAULT_POOL: ResourcePoolIn = {
  name: "Quarterly Planning Session",
  budget_inr: 2000000,
  doctors: 5,
  nurses: 10,
  anms: 15,
  ashas: 25,
  mobile_medical_units: 3,
  vaccine_doses: 8000,
  medicine_units: 1500,
  outreach_camps: 10,
};

function NumField({ label, value, onChange, unit }: { label: string; value: number; onChange: (v: number) => void; unit?: string }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-ink-600">{label}{unit && ` (${unit})`}</label>
      <input
        type="number"
        className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}

export default function ResourceOptimizer() {
  const [pool, setPool] = useState<ResourcePoolIn>(DEFAULT_POOL);
  const [result, setResult] = useState<ResourceOptimizationResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set<K extends keyof ResourcePoolIn>(key: K, value: ResourcePoolIn[K]) {
    setPool((p) => ({ ...p, [key]: value }));
  }

  async function optimize() {
    setRunning(true);
    setError(null);
    try {
      setResult(await api.optimizeResources(pool));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Resource Optimizer</h1>
        <p className="text-sm text-ink-500">
          Define the resources available this quarter — the optimizer allocates them across villages to maximize
          expected aggregate health impact (a transparent greedy heuristic, not a black box).
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader title="Available Resources" />
          <CardBody className="grid grid-cols-2 gap-3">
            <NumField label="Budget" unit="INR" value={pool.budget_inr} onChange={(v) => set("budget_inr", v)} />
            <NumField label="Doctors" value={pool.doctors} onChange={(v) => set("doctors", v)} />
            <NumField label="Nurses" value={pool.nurses} onChange={(v) => set("nurses", v)} />
            <NumField label="ANMs" value={pool.anms} onChange={(v) => set("anms", v)} />
            <NumField label="ASHA workers" value={pool.ashas} onChange={(v) => set("ashas", v)} />
            <NumField label="Mobile Medical Units" value={pool.mobile_medical_units} onChange={(v) => set("mobile_medical_units", v)} />
            <NumField label="Vaccine doses" value={pool.vaccine_doses} onChange={(v) => set("vaccine_doses", v)} />
            <NumField label="Medicine units" value={pool.medicine_units} onChange={(v) => set("medicine_units", v)} />
            <NumField label="Outreach camps" value={pool.outreach_camps} onChange={(v) => set("outreach_camps", v)} />
            <button onClick={optimize} disabled={running} className="col-span-2 mt-2 rounded-lg bg-brand-600 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50">
              {running ? "Optimizing…" : "Optimize Allocation"}
            </button>
            {error && <p className="col-span-2 text-xs text-red-600">{error}</p>}
          </CardBody>
        </Card>

        <div className="space-y-6 lg:col-span-2">
          {result && (
            <>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <StatTile label="Villages Funded" value={result.allocations.length} tone="brand" />
                <StatTile label="Population Covered" value={formatNumber(result.total_population_covered)} tone="good" />
                <StatTile label="Aggregate Impact" value={result.total_expected_impact.toFixed(0)} sublabel="model-estimated" tone="good" />
                <StatTile label="Budget Remaining" value={formatINR(result.remaining_budget_inr)} tone="neutral" />
              </div>

              <Card>
                <CardHeader title="Remaining Resources" />
                <CardBody className="grid grid-cols-3 gap-3 text-sm">
                  <div><p className="text-ink-500">MMUs</p><p className="font-semibold">{result.remaining_mmus}</p></div>
                  <div><p className="text-ink-500">Vaccine doses</p><p className="font-semibold">{formatNumber(result.remaining_vaccine_doses)}</p></div>
                  <div><p className="text-ink-500">Medicine units</p><p className="font-semibold">{formatNumber(result.remaining_medicine_units)}</p></div>
                </CardBody>
              </Card>

              <Card>
                <CardHeader title="Allocation Plan" subtitle="Ranked in the order resources were committed" />
                <CardBody className="overflow-x-auto p-0">
                  <table className="w-full min-w-[640px] text-sm">
                    <thead className="bg-ink-50 text-xs uppercase text-ink-500">
                      <tr>
                        <th className="px-4 py-2 text-left">#</th>
                        <th className="px-4 py-2 text-left">Village</th>
                        <th className="px-4 py-2 text-left">Intervention</th>
                        <th className="px-4 py-2 text-right">Budget</th>
                        <th className="px-4 py-2 text-right">Impact</th>
                        <th className="px-4 py-2 text-right">Population</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.allocations.map((a) => (
                        <tr key={a.village_id} className="border-t border-ink-100">
                          <td className="px-4 py-2">{a.rank}</td>
                          <td className="px-4 py-2 font-medium">{a.village_name}</td>
                          <td className="px-4 py-2">{a.intervention_name}</td>
                          <td className="px-4 py-2 text-right">{formatINR(a.allocated_budget_inr)}</td>
                          <td className="px-4 py-2 text-right">{a.expected_impact_score.toFixed(0)}</td>
                          <td className="px-4 py-2 text-right">{formatNumber(a.population_covered)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardBody>
              </Card>
            </>
          )}
          {!result && <p className="text-sm text-ink-500">Set your available resources and click Optimize Allocation.</p>}
        </div>
      </div>
    </div>
  );
}
