"use client";

import React, { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { RiskReportView } from "@/components/reports/RiskReportView";
import { RebalanceModal } from "@/components/rebalance/RebalanceModal";
import { ShieldAlert, RefreshCw, FileText } from "lucide-react";

export default function ReportsPage() {
  const { authenticated, user } = usePrivy();
  const activeAddress = authenticated && user?.wallet?.address 
    ? user.wallet.address 
    : "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045";

  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedAction, setSelectedAction] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const generateReport = () => {
    setLoading(true);
    fetch("http://localhost:8000/api/v1/risk/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        wallet_address: activeAddress,
        confidence_levels: [0.95, 0.99]
      }),
    })
      .then((res) => res.json())
      .then((data) => setReport(data))
      .catch((err) => console.error("Error generating risk report:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    generateReport();
  }, [activeAddress]);

  const handleSelectAction = (action: any) => {
    setSelectedAction(action);
    setIsModalOpen(true);
  };

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
            1-Day Value at Risk (VaR), Expected Shortfall (CVaR), and algorithmic rebalance proposals
          </p>
        </div>

        <button
          onClick={generateReport}
          disabled={loading}
          className="btn btn-primary"
          style={{ gap: "8px" }}
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          {loading ? "Calculating Tail Risk..." : "Generate Fresh Report"}
        </button>
      </div>

      {loading && !report ? (
        <div className="glass-card" style={{ padding: "60px", textAlign: "center", color: "var(--text-muted)" }}>
          <RefreshCw className="animate-spin" size={28} style={{ margin: "0 auto 12px auto" }} />
          Computing 95% & 99% parametric & historical tail-risk quantiles...
        </div>
      ) : report ? (
        <RiskReportView
          report={report}
          onSelectRebalanceAction={handleSelectAction}
        />
      ) : null}

      <RebalanceModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        action={selectedAction}
      />
    </div>
  );
}
