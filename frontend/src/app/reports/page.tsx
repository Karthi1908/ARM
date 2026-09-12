"use client";

import React, { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { useActiveWallet } from "@/context/WalletContext";
import { RiskReportView } from "@/components/reports/RiskReportView";
import { RebalanceModal } from "@/components/rebalance/RebalanceModal";
import { ShieldAlert, RefreshCw, FileText, Wallet } from "lucide-react";

export default function ReportsPage() {
  const { login } = usePrivy();
  const { activeAddress } = useActiveWallet();

  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedAction, setSelectedAction] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const generateReport = () => {
    if (!activeAddress) {
      setReport(null);
      return;
    }
    setLoading(true);
    fetch("/api/v1/risk/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        wallet_address: activeAddress,
        confidence_levels: [0.95, 0.99]
      }),
    })
      .then((res) => res.json())
      .then((data) => setReport(data))
      .catch((err) => {
        console.error("Error generating risk report:", err);
        setReport(null);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    generateReport();
  }, [activeAddress]);

  const handleSelectAction = (action: any) => {
    setSelectedAction(action);
    setIsModalOpen(true);
  };

  if (!activeAddress) {
    return (
      <div className="glass-card" style={{ padding: "48px 32px", textAlign: "center", maxWidth: "600px", margin: "40px auto" }}>
        <FileText size={36} color="var(--accent-secondary)" style={{ margin: "0 auto 16px auto" }} />
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.5rem", fontWeight: 700, marginBottom: "12px" }}>
          Risk Reports & VaR
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "24px" }}>
          Connect your wallet or enter a public address to compute 1-day 95% & 99% Value at Risk (VaR) and Expected Shortfall from actual balances.
        </p>
        <button onClick={login} className="btn btn-primary" style={{ padding: "10px 24px" }}>
          <Wallet size={16} /> Connect Wallet
        </button>
      </div>
    );
  }

  return (
    <div>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "16px",
        marginBottom: "24px"
      }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: "2rem", fontWeight: 800 }}>
            Institutional Risk Reports
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            1-Day Value at Risk (VaR), Expected Shortfall (CVaR), and algorithmic rebalance proposals from actual holdings
          </p>
        </div>

        <button
          onClick={generateReport}
          disabled={loading}
          className="btn btn-primary"
          style={{ gap: "8px" }}
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          {loading ? "Recomputing Risk Metrics..." : "Recompute Risk Report"}
        </button>
      </div>

      {loading && !report ? (
        <div className="glass-card" style={{ padding: "60px", textAlign: "center", color: "var(--text-muted)" }}>
          <ShieldAlert className="animate-spin" size={32} style={{ margin: "0 auto 12px auto", color: "var(--accent-primary)" }} />
          Running parametric and historical Monte Carlo simulation on actual positions...
        </div>
      ) : report ? (
        <RiskReportView
          report={report}
          onSelectRebalanceAction={handleSelectAction}
        />
      ) : (
        <div className="glass-card" style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
          No risk report generated yet. Click &quot;Recompute Risk Report&quot; above.
        </div>
      )}

      {/* Rebalance Swaps Modal */}
      {selectedAction && (
        <RebalanceModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          action={selectedAction}
          walletAddress={activeAddress}
        />
      )}
    </div>
  );
}
