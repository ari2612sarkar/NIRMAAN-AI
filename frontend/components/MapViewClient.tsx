"use client";

import dynamic from "next/dynamic";
import type { MapBin } from "@/lib/api";

const MapView = dynamic(() => import("./MapView"), {
  ssr: false,
  loading: () => <div className="h-full w-full flex items-center justify-center text-muted text-sm">Loading map…</div>,
});

export function MapViewClient({ bins }: { bins: MapBin[] }) {
  return <MapView bins={bins} />;
}
