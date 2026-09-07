import type { Metadata } from "next";
import "@/styles/theme.css";
import { Providers } from "./providers";
import { Header } from "@/components/layout/Header";
import { ProvenanceAlert } from "@/components/layout/ProvenanceAlert";

export const metadata: Metadata = {
  title: "Agentic Risk Manager | Institutional Crypto Risk Engine",
  description: "Non-custodial crypto portfolio risk manager, Greek factor decomposition, VaR, Expected Shortfall, and consensual rebalancing.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
            <ProvenanceAlert />
            <Header />
            <main style={{ flex: 1, maxWidth: "1400px", width: "100%", margin: "0 auto", padding: "24px" }}>
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
