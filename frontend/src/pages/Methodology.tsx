import type { ReactNode } from "react";
import { useApi } from "@/lib/useApi";
import { api } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <Card>
      <CardHeader title={title} />
      <CardBody className="space-y-2 text-sm text-ink-700">{children}</CardBody>
    </Card>
  );
}

export default function Methodology() {
  const meta = useApi(() => api.methodology(), []);
  const m = meta.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-ink-900">Methodology</h1>
        <p className="text-sm text-ink-500">
          RuralCare AI is a decision-support system, not a black box. Every score, prediction and recommendation below
          is computed transparently from structured data — GenAI is used only to narrate results, never to invent
          statistics, diagnose patients, or assert unproven causal relationships.
        </p>
      </div>

      {meta.loading && <p className="text-sm text-ink-500">Loading…</p>}
      {m && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Section id="gap" title="1. Healthcare Gap Index">
            <p>{m.gap_index.description}</p>
            <table className="mt-2 w-full text-xs">
              <tbody>
                {Object.entries(m.gap_index.weights as Record<string, number>).map(([k, v]) => (
                  <tr key={k} className="border-t border-ink-100">
                    <td className="py-1 capitalize">{k}</td>
                    <td className="py-1 text-right font-semibold">{(v * 100).toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-2 text-xs text-ink-500">
              Risk categories: {Object.entries(m.gap_index.risk_categories as Record<string, string>).map(([k, v]) => `${k} ${v}`).join(" · ")}
            </p>
          </Section>

          <Section id="paradox" title="2. Infrastructure-Outcome Paradox">
            <p>{m.paradox_detection.description}</p>
            <p className="text-xs text-ink-500">
              Infrastructure high threshold: {m.paradox_detection.infrastructure_high_threshold} · Weak dimension threshold: {m.paradox_detection.weak_dimension_threshold}
            </p>
          </Section>

          <Section id="risk" title="3. Risk Prediction (ML)">
            <p>{m.risk_prediction.description}</p>
            <p className="text-xs text-ink-500">Model: {m.risk_prediction.model}</p>
          </Section>

          <Section id="xai" title="4. Explainable AI">
            <p>{m.explainability.description}</p>
          </Section>

          <Section id="priority" title="5. Village Prioritization">
            <p>{m.prioritization.description}</p>
          </Section>

          <Section id="intervention" title="6. Intervention Recommendation">
            <p>{m.intervention_engine.description.replace("%s", String(m.intervention_engine.infra_gap_threshold))}</p>
          </Section>

          <Section id="optimizer" title="7. Resource Optimization">
            <p>{m.resource_optimization.description}</p>
          </Section>

          <Section id="simulation" title="8. What-If Simulation">
            <p>{m.simulation.description}</p>
          </Section>

          <Section id="mismatch" title="9. Resource Mismatch Detection">
            <p>
              Overload threshold: {m.resource_mismatch.overload_utilization_pct}% of capacity · Underutilized threshold:{" "}
              {m.resource_mismatch.underutilized_utilization_pct}% of capacity.
            </p>
          </Section>

          <Section id="sources" title="10. Data Sources & Geographic Harmonization">
            <ul className="list-disc space-y-1 pl-5 text-xs">
              {Object.entries(m.data_sources as Record<string, string>)
                .filter(([k]) => k !== "note")
                .map(([k, v]) => (
                  <li key={k}><b>{k}</b>: {v}</li>
                ))}
            </ul>
            <p className="mt-2 text-xs text-ink-500">{m.data_sources.note}</p>
          </Section>
        </div>
      )}
    </div>
  );
}
