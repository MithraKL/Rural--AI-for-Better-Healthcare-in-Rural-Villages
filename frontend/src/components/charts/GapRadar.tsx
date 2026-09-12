import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from "recharts";
import type { GapScore } from "@/types";

export default function GapRadar({ scores }: { scores: GapScore }) {
  const data = [
    { dimension: "Infrastructure", value: scores.infrastructure_score },
    { dimension: "Workforce", value: scores.workforce_score },
    { dimension: "Service", value: scores.service_score },
    { dimension: "Utilization", value: scores.utilization_score },
    { dimension: "Outcomes", value: scores.outcome_score },
    { dimension: "Nutrition", value: scores.nutrition_score },
    { dimension: "Accessibility", value: scores.accessibility_score },
  ];
  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} outerRadius="75%">
        <PolarGrid stroke="#e2e8f0" />
        <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11, fill: "#334155" }} />
        <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 9 }} axisLine={false} />
        <Radar dataKey="value" stroke="#137a73" fill="#18948b" fillOpacity={0.35} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
