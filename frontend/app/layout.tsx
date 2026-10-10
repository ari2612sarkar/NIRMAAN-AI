import type { Metadata } from "next";
import "./globals.css";
import "leaflet/dist/leaflet.css";

export const metadata: Metadata = {
  title: "NIRMAAN AI — Waste Intelligence & Cost Optimization",
  description:
    "Predict waste, optimize collection, prioritize maintenance, and simulate cost savings — an AI operations platform for municipal waste management.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-background text-foreground antialiased">{children}</body>
    </html>
  );
}
