"use client";

import React, { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { HoldingsTable, PositionItem } from "@/components/dashboard/HoldingsTable";
import { SingleRiskDrawer } from "@/components/risk/SingleRiskDrawer";
import { NetGreeksCards } from "@/components/dashboard/NetGreeksCards";
import { CopilotDrawer } from "@/components/copilot/CopilotDrawer";
import { TrendingUp, ShieldAlert, ArrowRight, MessageSquareCode } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { authenticated, user } = usePrivy();
  const activeAddress = authenticated && user?.wallet?.address 
    ? user.wallet.address 
    : "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045";

  const [portfolio, setPortfolio] = useState<{ total_value_usd: number; positions: PositionItem[] }>({
    total_value_usd: 0,
    positions: []
  });
  const [selectedPosition, setSelectedPosition] = useState<PositionItem | null>(null);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchPortfolio = () => {
    setLoading(true);
    fetch(`http://localhost:8000/api/v1/portfolio/${activeAddress}`)
      .then((res) => res.json())
      .then((data) => {
        setPortfolio({
          total_value_usd: data.total_value_usd || 0,
          positions: data.positions || []
        });
      })
      .catch((err) => console.error("Error fetching portfolio:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPortfolio();
    const handleUpdate = () => fetchPortfolio();
    window.addEventListener("portfolio-updated", handleUpdate);
    return () => window.removeEventListener("portfolio-updated", handleUpdate);
  }, [activeAddress]);

  return (
    <div>
      {/* Executive Portfolio Banner */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "16px",
        marginBottom: "24px"
      }}>
        <div>
          <div style={{ color: "var(--text-secondary)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "4px" }}>
            Total Portfolio Valuation (USD)
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: "12px" }}>
            <span style={{ fontSize: "2.5rem", fontWeight: 800, fontFamily: "var(--font-display)" }} className="mono-num">
              ${portfolio.total_value_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="badge badge-positive">
              <TrendingUp size={12} /> Active Multi-Chain Book
            </span>
          </div>
        </div>

        {/* Quick Action Buttons */}
        <div style={{ display: "flex", gap: "10px" }}>
          <button onClick={() => setIsCopilotOpen(true)} className="btn btn-secondary" style={{ gap: "8px" }}>
            <MessageSquareCode size={16} color="var(--accent-secondary)" />
            AI Risk Copilot
          </button>
          <Link href="/reports" className="btn btn-primary" style={{ gap: "8px" }}>
            <ShieldAlert size={16} />
            Generate Risk Report
          </Link>
        </div>
      </div>

      {/* Whole-Portfolio Net Greeks & Ratios */}
      <NetGreeksCards walletAddress={activeAddress} />

      {/* Unified Holdings Blotter */}
      <HoldingsTable
        positions={portfolio.positions}
        onSelectPosition={(pos) => setSelectedPosition(pos)}
        selectedAssetId={selectedPosition?.asset_id}
      />

      {/* Single-Deal Risk Analytics Drawer */}
      {selectedPosition && (
        <SingleRiskDrawer
          assetId={selectedPosition.asset_id}
          assetName={selectedPosition.name}
          onClose={() => setSelectedPosition(null)}
        />
      )}

      {/* Gemini AI Copilot Drawer */}
      <CopilotDrawer
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        walletAddress={activeAddress}
      />
    </div>
  );
}
