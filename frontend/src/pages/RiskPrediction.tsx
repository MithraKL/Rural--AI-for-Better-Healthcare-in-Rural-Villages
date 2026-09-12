import { useState } from "react";
import { Link } from "react-router-dom";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/Badge";
import DriverBars from "@/components/charts/DriverBars";

export default function RiskPrediction() {
  const [riskFilter, setRiskFilter] = useState("");
  const [selected, setSelected] = useState<number | null>(null);

  const risk = useApi(() => api.riskList({ risk_category: riskFilter || undefined }), [riskFilter]);
  const selectedRow = risk.data?.find((r) => r.village_id === selected);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Risk & Prediction</h1>
        <p className="text-sm text-ink-500">
          ML-predicted next-quarter risk for every village (RandomForest over historical Gap Index trends), not an LLM guess.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader
            title="Village Risk Forecast"
            action={
              <select className="rounded-lg border border-ink-200 px-2 py-1 text-xs" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
                {["", "CRITICAL", "HIGH", "MODERATE", "LOW"].map((r) => (
                  <option key={r} value={r}>{r || "All"}</option>
                ))}
              </select>
            }
          />
          <CardBody className="max-h-[600px] overflow-y-auto p-0">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-ink-50 text-xs uppercase text-ink-500">
                <tr>
                  <th className="px-4 py-2 text-left">Village</th>
                  <th className="px-4 py-2 text-right">Current</th>
                  <th className="px-4 py-2 text-right">Predicted</th>
                  <th className="px-4 py-2 text-left">Trend</th>
                  <th className="px-4 py-2 text-left">Category</th>
                  <th className="px-4 py-2 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {risk.data?.map((r) => (
                  <tr
                    key={r.village_id}
                    className={`cursor-pointer border-t border-ink-100 hover:bg-ink-50 ${selected === r.village_id ? "bg-brand-500/5" : ""}`}
                    onClick={() => setSelected(r.village_id)}
                  >
                    <td className="px-4 py-2 font-medium">#{r.village_id}</td>
                    <td className="px-4 py-2 text-right">{r.current_risk.toFixed(0)}</td>
                    <td className="px-4 py-2 text-right font-semibold">{r.predicted_risk.toFixed(0)}</td>
                    <td className="px-4 py-2 capitalize">{r.trend_direction}</td>
                    <td className="px-4 py-2"><RiskBadge category={r.risk_category} size="sm" /></td>
                    <td className="px-4 py-2 text-right">{r.insufficient_data ? "—" : `${(r.confidence * 100).toFixed(0)}%`}</td>
                  </tr>
                ))}
                {risk.loading && <tr><td colSpan={6} className="px-4 py-6 text-center text-ink-500">Loading…</td></tr>}
              </tbody>
            </table>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Why?" subtitle="Select a village row to see its risk drivers" />
          <CardBody>
            {!selectedRow && <p className="text-sm text-ink-500">Click a village on the left.</p>}
            {selectedRow?.insufficient_data && <p className="text-sm text-ink-500">Insufficient historical data for reliable prediction.</p>}
            {selectedRow && !selectedRow.insufficient_data && (
              <>
                <DriverBars factors={selectedRow.factors} />
                <Link to={`/villages/${selectedRow.village_id}`} className="mt-4 inline-block text-sm font-semibold text-brand-700 hover:underline">
                  View full village profile →
                </Link>
              </>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
