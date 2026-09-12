import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { formatINR, formatNumber } from "@/lib/format";
import type { SimulationResult } from "@/types";

function Slider({ label, value, onChange, max, step = 1, unit = "" }: { label: string; value: number; onChange: (v: number) => void; max: number; step?: number; unit?: string }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs font-medium text-ink-600">
        <span>{label}</span>
        <span className="text-ink-900">{value}{unit}</span>
      </div>
      <input type="range" min={0} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-brand-600" />
    </div>
  );
}

export default function WhatIfSimulator() {
  const [params] = useSearchParams();
  const [villageId, setVillageId] = useState<number | null>(params.get("village") ? Number(params.get("village")) : null);
  const [selectedIds, setSelectedIds] = useState<number[]>(
    params.get("interventions") ? params.get("interventions")!.split(",").map(Number) : []
  );
  const [scenarioName, setScenarioName] = useState("Scenario A");
  const [workers, setWorkers] = useState(2);
  const [mmus, setMmus] = useState(0);
  const [vaccineDoses, setVaccineDoses] = useState(0);
  const [medicineUnits, setMedicineUnits] = useState(0);
  const [outreach, setOutreach] = useState(1);
  const [budget, setBudget] = useState(0);
  const [scenarios, setScenarios] = useState<SimulationResult[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const villages = useApi(() => api.villages(), []);
  const interventions = useApi(() => (villageId ? api.interventions(villageId) : Promise.resolve([])), [villageId]);

  useEffect(() => setScenarios([]), [villageId]);

  function toggle(id: number) {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  async function runSimulation() {
    if (!villageId) return;
    setRunning(true);
    setError(null);
    try {
      const result = await api.simulate({
        village_id: villageId,
        scenario_name: scenarioName || `Scenario ${scenarios.length + 1}`,
        intervention_ids: selectedIds,
        healthcare_workers: workers,
        mobile_medical_units: mmus,
        vaccine_doses: vaccineDoses,
        medicine_units: medicineUnits,
        outreach_camps_per_quarter: outreach,
        budget_inr: budget,
      });
      setScenarios((prev) => [...prev, result]);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  const best = scenarios.length
    ? scenarios.reduce((a, b) => (b.baseline_risk - b.projected_risk > a.baseline_risk - a.projected_risk ? b : a))
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-ink-900">What-If Impact Simulator</h1>
        <p className="text-sm text-ink-500">
          Select interventions and resource dosage, simulate the projected effect, and compare scenarios side by side.
          All results are model-estimated projections, not guaranteed outcomes.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader title="Scenario Setup" />
          <CardBody className="space-y-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-ink-600">Village</label>
              <select className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" value={villageId ?? ""} onChange={(e) => { setVillageId(Number(e.target.value)); setSelectedIds([]); }}>
                <option value="">Select village…</option>
                {villages.data?.map((v) => <option key={v.id} value={v.id}>{v.name} — {v.district_name}</option>)}
              </select>
            </div>

            {villageId && (
              <div>
                <label className="mb-1 block text-xs font-medium text-ink-600">Interventions</label>
                <div className="space-y-1.5">
                  {interventions.data?.map((opt) => (
                    <label key={opt.id} className="flex items-center gap-2 rounded-md border border-ink-200 px-2 py-1.5 text-xs">
                      <input type="checkbox" checked={selectedIds.includes(opt.id)} onChange={() => toggle(opt.id)} />
                      {opt.intervention_name} <span className="text-ink-400">({opt.cost_level})</span>
                    </label>
                  ))}
                  {interventions.data?.length === 0 && <p className="text-xs text-ink-400">No detected problems for this village.</p>}
                </div>
              </div>
            )}

            <Slider label="Healthcare workers deployed" value={workers} max={10} onChange={setWorkers} />
            <Slider label="Mobile Medical Units" value={mmus} max={5} onChange={setMmus} />
            <Slider label="Vaccine doses allocated" value={vaccineDoses} max={2000} step={50} onChange={setVaccineDoses} />
            <Slider label="Medicine units allocated" value={medicineUnits} max={500} step={10} onChange={setMedicineUnits} />
            <Slider label="Outreach camps / quarter" value={outreach} max={6} onChange={setOutreach} />
            <Slider label="Budget allocated" value={budget} max={1000000} step={10000} unit=" ₹" onChange={setBudget} />

            <div>
              <label className="mb-1 block text-xs font-medium text-ink-600">Scenario name</label>
              <input className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" value={scenarioName} onChange={(e) => setScenarioName(e.target.value)} />
            </div>

            <button
              disabled={!villageId || running}
              onClick={runSimulation}
              className="w-full rounded-lg bg-brand-600 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {running ? "Simulating…" : "Run Simulation"}
            </button>
            {error && <p className="text-xs text-red-600">{error}</p>}
          </CardBody>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Scenario Comparison" subtitle="Before → Projected, across every scenario you've run" />
          <CardBody className="overflow-x-auto">
            {scenarios.length === 0 && <p className="text-sm text-ink-500">Run a scenario to see projected impact here.</p>}
            {scenarios.length > 0 && (
              <table className="w-full min-w-[640px] text-sm">
                <thead className="text-xs uppercase text-ink-500">
                  <tr>
                    <th className="py-2 text-left">Scenario</th>
                    <th className="py-2 text-right">Risk (before → after)</th>
                    <th className="py-2 text-right">Utilization</th>
                    <th className="py-2 text-right">Immunization</th>
                    <th className="py-2 text-right">Cost</th>
                    <th className="py-2 text-right">Time</th>
                    <th className="py-2 text-right">Coverage</th>
                  </tr>
                </thead>
                <tbody>
                  {scenarios.map((s, idx) => (
                    <tr key={idx} className={`border-t border-ink-100 ${s === best ? "bg-emerald-50" : ""}`}>
                      <td className="py-2 font-medium">
                        {s.scenario_name} {s === best && <span className="ml-1 rounded-full bg-emerald-600 px-2 py-0.5 text-[10px] font-bold text-white">BEST</span>}
                      </td>
                      <td className="py-2 text-right">{s.baseline_risk.toFixed(0)} → <b>{s.projected_risk.toFixed(0)}</b></td>
                      <td className="py-2 text-right">{s.baseline_utilization_pct.toFixed(0)}% → <b>{s.projected_utilization_pct.toFixed(0)}%</b></td>
                      <td className="py-2 text-right">{s.baseline_immunization_pct.toFixed(0)}% → <b>{s.projected_immunization_pct.toFixed(0)}%</b></td>
                      <td className="py-2 text-right">{formatINR(s.cost_estimate_inr)}</td>
                      <td className="py-2 text-right">{s.time_months} mo</td>
                      <td className="py-2 text-right">{formatNumber(s.population_covered)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {scenarios.length > 0 && (
              <p className="mt-3 text-xs text-ink-400">{scenarios[0].disclaimer}</p>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
