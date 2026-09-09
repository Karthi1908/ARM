"use client";

import React, { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { useActiveWallet } from "@/context/WalletContext";
import { HoldingsTable, PositionItem } from "@/components/dashboard/HoldingsTable";
import { SingleRiskDrawer } from "@/components/risk/SingleRiskDrawer";
import { NetGreeksCards } from "@/components/dashboard/NetGreeksCards";
import { CopilotDrawer } from "@/components/copilot/CopilotDrawer";
import { RebalanceModal } from "@/components/rebalance/RebalanceModal";
import { TrendingUp, ShieldAlert, ArrowRight, MessageSquareCode, Wallet, Search, RefreshCw } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { login } = usePrivy();
  const { activeAddress, setActiveAddress, isConnected, isSyncing, syncPortfolio } = useActiveWallet();

  const [portfolio, setPortfolio] = useState<{ total_value_usd: number; positions: PositionItem[] }>({
    total_value_usd: 0,
    positions: []
  });
  const [selectedPosition, setSelectedPosition] = useState<PositionItem | null>(null);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [selectedHedgeAction, setSelectedHedgeAction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [manualInput, setManualInput] = useState("");

  const fetchPortfolio = () => {
    if (!activeAddress) {
      setPortfolio({ total_value_usd: 0, positions: [] });
      setLoading(false);
      return;
    }
    setLoading(true);
    fetch(`http://localhost:8000/api/v1/portfolio/${activeAddress}`)
      .then((res) => res.json())
      .then((data) => {
        setPortfolio({
          total_value_usd: data.total_value_usd || 0,
          positions: Array.isArray(data.positions) ? data.positions : []
        });
      })
      .catch((err) => {
        console.error("Error fetching live portfolio:", err);
        setPortfolio({ total_value_usd: 0, positions: [] });
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPortfolio();
    const handleUpdate = () => fetchPortfolio();
    window.addEventListener("portfolio-updated", handleUpdate);
    return () => window.removeEventListener("portfolio-updated", handleUpdate);
  }, [activeAddress]);

  const handleInspect = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualInput.trim()) {
      setActiveAddress(manualInput.trim());
    }
  };

  return (
    <div>
      {/* If No Address Connected or Inspected: Prompt User */}
      {!activeAddress ? (
        <div className="glass-card" style={{ padding: "48px 32px", textAlign: "center", maxWidth: "680px", margin: "40px auto" }}>
          <div style={{
            width: "56px",
            height: "56px",
            borderRadius: "16px",
            background: "var(--accent-gradient)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 20px auto",
            boxShadow: "0 0 24px rgba(99, 102, 241, 0.4)"
          }}>
            <Wallet size={28} color="#fff" />
          </div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.75rem", fontWeight: 800, marginBottom: "12px" }}>
            Connect Your Wallet
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", lineHeight: 1.6, marginBottom: "28px" }}>
            Connect via Privy or inspect any public EVM address to scan actual live token holdings across Ethereum, Arbitrum, Optimism, Base, and Polygon with zero simulated data.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px", alignItems: "center" }}>
            <button onClick={login} className="btn btn-primary" style={{ padding: "12px 28px", fontSize: "1rem", width: "100%", maxWidth: "320px" }}>
              <Wallet size={18} />
              Connect Wallet (Privy)
            </button>

            <div style={{ display: "flex", alignItems: "center", gap: "12px", width: "100%", maxWidth: "320px" }}>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }}></div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase" }}>or inspect public address</span>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }}></div>
            </div>

            <form onSubmit={handleInspect} style={{ display: "flex", gap: "8px", width: "100%", maxWidth: "420px" }}>
              <input
                type="text"
                placeholder="0x... EVM address or vitalik.eth"
                value={manualInput}
                onChange={(e) => setManualInput(e.target.value)}
                style={{
                  flex: 1,
                  padding: "10px 14px",
                  background: "var(--bg-elevated)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)",
                  fontSize: "0.9rem"
                }}
              />
              <button type="submit" className="btn btn-secondary" style={{ padding: "10px 16px" }}>
                <Search size={16} />
                Inspect
              </button>
            </form>
          </div>
        </div>
      ) : (
        <>
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
                Live Portfolio Valuation (USD)
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "12px" }}>
                <span style={{ fontSize: "2.5rem", fontWeight: 800, fontFamily: "var(--font-display)" }} className="mono-num">
                  ${portfolio.total_value_usd.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <span className={`badge ${portfolio.total_value_usd > 0 ? "badge-positive" : "badge-neutral"}`}>
                  <TrendingUp size={12} />
                  {portfolio.positions.length} Live On-Chain Positions
                </span>
              </div>
            </div>

            {/* Quick Action Buttons */}
            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              <button
                onClick={syncPortfolio}
                disabled={isSyncing}
                className="btn btn-secondary"
                style={{ gap: "6px" }}
              >
                <RefreshCw size={14} className={isSyncing ? "animate-spin" : ""} />
                {isSyncing ? "Scanning 5 Chains..." : "Sync Live Holdings"}
              </button>
              <button onClick={() => setIsCopilotOpen(true)} className="btn btn-secondary" style={{ gap: "8px" }}>
                <MessageSquareCode size={16} color="var(--accent-secondary)" />
                AI Risk Copilot
              </button>
              <Link href="/reports" className="btn btn-primary" style={{ gap: "8px" }}>
                <ShieldAlert size={16} />
                Risk Report & VaR
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
            onHedgePosition={(pos) => {
              setSelectedHedgeAction({
                action_type: "hedge_to_usdc",
                from_token: pos.symbol,
                to_token: "USDC",
                amount: String(pos.quantity),
                recommended_venue: "uniswap",
                usd_value: pos.total_value_usd,
              });
            }}
          />
        </>
      )}

      {/* Single-Deal Risk Analytics Drawer */}
      {selectedPosition && (
        <SingleRiskDrawer
          assetId={selectedPosition.asset_id}
          assetName={selectedPosition.name}
          onClose={() => setSelectedPosition(null)}
        />
      )}

      {/* Gemini AI Copilot Drawer */}
      {activeAddress && (
        <CopilotDrawer
          isOpen={isCopilotOpen}
          onClose={() => setIsCopilotOpen(false)}
          walletAddress={activeAddress}
        />
      )}

      {/* Quick Holdings Row Hedge Modal */}
      {selectedHedgeAction && (
        <RebalanceModal
          isOpen={Boolean(selectedHedgeAction)}
          onClose={() => setSelectedHedgeAction(null)}
          action={selectedHedgeAction}
          walletAddress={activeAddress || undefined}
        />
      )}
    </div>
  );
}
