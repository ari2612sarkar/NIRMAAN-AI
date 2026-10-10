"use client";

import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import type { MapBin } from "@/lib/api";

const CATEGORY_COLOR: Record<string, string> = {
  mixed: "#8a99ab",
  wet: "#5b8def",
  dry: "#e8b84b",
  recyclable: "#35d0ac",
};

export default function MapView({ bins }: { bins: MapBin[] }) {
  if (bins.length === 0) return null;
  const center: [number, number] = [bins[0].latitude, bins[0].longitude];

  return (
    <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }} scrollWheelZoom={false}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        className="map-tiles-dark"
      />
      {bins.map((b) => (
        <CircleMarker
          key={b.bin_code}
          center={[b.latitude, b.longitude]}
          radius={b.overflow_risk ? 8 : 5}
          pathOptions={{
            color: b.overflow_risk ? "#e2655b" : CATEGORY_COLOR[b.waste_category] || "#8a99ab",
            fillOpacity: 0.7,
            weight: b.overflow_risk ? 2 : 1,
          }}
        >
          <Popup>
            <div style={{ fontSize: 12 }}>
              <strong>{b.bin_code}</strong> — {b.waste_category}
              <br />
              {b.location_name}
              <br />
              {b.zone_name}
              {b.overflow_risk && (
                <>
                  <br />
                  <span style={{ color: "#e2655b" }}>⚠ Overflow risk</span>
                </>
              )}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
