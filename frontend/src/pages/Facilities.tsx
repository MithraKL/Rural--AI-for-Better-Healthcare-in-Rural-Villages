import { useState } from "react";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

const MISMATCH_TONE: Record<string, { label: string; className: string }> = {
  OVERLOADED: { label: "Overloaded", className: "bg-red-100 text-red-800" },
  UNDER_RESOURCED: { label: "Under-resourced", className: "bg-orange-100 text-orange-800" },
  UNDERUTILIZED: { label: "Underutilized", className: "bg-amber-100 text-amber-800" },
  BALANCED: { label: "Balanced", className: "bg-emerald-100 text-emerald-800" },
};

export default function Facilities() {
  const [filter, setFilter] = useState("");
  const mismatch = useApi(() => api.facilityMismatch(), []);

  const rows = (mismatch.data ?? []).filter((f) => !filter || f.mismatch_type === filter);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Facilities</h1>
        <p className="text-sm text-ink-500">
          Resource wastage / mismatch detection — flags facilities whose staffing and patient load look imbalanced.
          These are planning suggestions requiring administrative validation, never automatic transfer orders.
        </p>
      </div>

      <Card>
        <CardHeader
          title="Facility Load & Staffing"
          action={
            <select className="rounded-lg border border-ink-200 px-2 py-1 text-xs" value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="">All</option>
              <option value="OVERLOADED">Overloaded</option>
              <option value="UNDER_RESOURCED">Under-resourced</option>
              <option value="UNDERUTILIZED">Underutilized</option>
              <option value="BALANCED">Balanced</option>
            </select>
          }
        />
        <CardBody className="overflow-x-auto p-0">
          <table className="w-full min-w-[760px] text-sm">
            <thead className="bg-ink-50 text-xs uppercase text-ink-500">
              <tr>
                <th className="px-4 py-2 text-left">Facility</th>
                <th className="px-4 py-2 text-left">Village</th>
                <th className="px-4 py-2 text-right">Doctors in Position</th>
                <th className="px-4 py-2 text-right">Utilization</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((f) => (
                <tr key={f.facility_id} className="border-t border-ink-100">
                  <td className="px-4 py-2 font-medium">{f.facility_name}</td>
                  <td className="px-4 py-2 text-ink-600">{f.village_name}</td>
                  <td className="px-4 py-2 text-right">{f.doctors_in_position}</td>
                  <td className="px-4 py-2 text-right">{f.utilization_pct?.toFixed(0) ?? "—"}%</td>
                  <td className="px-4 py-2">
                    <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${MISMATCH_TONE[f.mismatch_type].className}`}>
                      {MISMATCH_TONE[f.mismatch_type].label}
                    </span>
                  </td>
                  <td className="max-w-md px-4 py-2 text-xs text-ink-600">{f.note}</td>
                </tr>
              ))}
              {mismatch.loading && <tr><td colSpan={6} className="px-4 py-6 text-center text-ink-500">Loading…</td></tr>}
            </tbody>
          </table>
        </CardBody>
      </Card>
      <Badge tone="neutral">Planning suggestions require administrative validation before any staff reassignment.</Badge>
    </div>
  );
}
