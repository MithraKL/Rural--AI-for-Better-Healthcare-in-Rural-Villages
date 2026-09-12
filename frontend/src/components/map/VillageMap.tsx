import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from "react-leaflet";
import { useEffect } from "react";
import type { VillageSummary } from "@/types";
import { RISK_MAP_COLOR } from "@/lib/format";

function FitBounds({ villages }: { villages: VillageSummary[] }) {
  const map = useMap();
  useEffect(() => {
    const pts = villages.filter((v) => v.latitude && v.longitude).map((v) => [v.latitude!, v.longitude!] as [number, number]);
    if (pts.length > 0) {
      map.fitBounds(pts, { padding: [30, 30], maxZoom: 9 });
    }
  }, [villages, map]);
  return null;
}

export default function VillageMap({
  villages, onSelect, height = 420,
}: { villages: VillageSummary[]; onSelect?: (v: VillageSummary) => void; height?: number }) {
  const withCoords = villages.filter((v) => v.latitude && v.longitude);
  const center: [number, number] = withCoords.length
    ? [withCoords[0].latitude!, withCoords[0].longitude!]
    : [25.5, 80.5];

  return (
    <div style={{ height }}>
      <MapContainer center={center} zoom={7} scrollWheelZoom style={{ height: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds villages={withCoords} />
        {withCoords.map((v) => (
          <CircleMarker
            key={v.id}
            center={[v.latitude!, v.longitude!]}
            radius={Math.max(5, Math.min(14, Math.sqrt(v.population) / 12))}
            pathOptions={{
              color: RISK_MAP_COLOR[v.risk_category ?? "MODERATE"],
              fillColor: RISK_MAP_COLOR[v.risk_category ?? "MODERATE"],
              fillOpacity: 0.65,
              weight: v.is_paradox ? 3 : 1,
            }}
            eventHandlers={{ click: () => onSelect?.(v) }}
          >
            <Tooltip direction="top">
              <div className="text-xs">
                <p className="font-semibold">{v.name}{v.is_paradox ? " ⚠" : ""}</p>
                <p>{v.district_name}</p>
                <p>Risk: {v.risk_category} ({v.overall_gap_score?.toFixed(0)})</p>
                <p>Population: {v.population.toLocaleString()}</p>
                {v.is_paradox && <p className="font-semibold text-amber-700">Infrastructure-Outcome Paradox</p>}
              </div>
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
