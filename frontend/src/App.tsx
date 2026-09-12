import { Routes, Route } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import Overview from "@/pages/Overview";
import VillageIntelligence from "@/pages/VillageIntelligence";
import VillageProfile from "@/pages/VillageProfile";
import RiskPrediction from "@/pages/RiskPrediction";
import HiddenGaps from "@/pages/HiddenGaps";
import InterventionPlanner from "@/pages/InterventionPlanner";
import WhatIfSimulator from "@/pages/WhatIfSimulator";
import ResourceOptimizer from "@/pages/ResourceOptimizer";
import Facilities from "@/pages/Facilities";
import DataExplorer from "@/pages/DataExplorer";
import Methodology from "@/pages/Methodology";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Overview />} />
        <Route path="/villages" element={<VillageIntelligence />} />
        <Route path="/villages/:id" element={<VillageProfile />} />
        <Route path="/risk" element={<RiskPrediction />} />
        <Route path="/hidden-gaps" element={<HiddenGaps />} />
        <Route path="/interventions" element={<InterventionPlanner />} />
        <Route path="/simulator" element={<WhatIfSimulator />} />
        <Route path="/resources" element={<ResourceOptimizer />} />
        <Route path="/facilities" element={<Facilities />} />
        <Route path="/data" element={<DataExplorer />} />
        <Route path="/methodology" element={<Methodology />} />
      </Route>
    </Routes>
  );
}
